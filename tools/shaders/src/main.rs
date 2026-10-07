use std::{env,fs};
fn main() {
    let args: Vec<_> = env::args().collect();
    let stage = if args[1].ends_with(".vert") { naga::ShaderStage::Vertex } else { naga::ShaderStage::Fragment };
    let source = fs::read_to_string(&args[1]).unwrap();
    let module = naga::front::glsl::Frontend::default().parse(&naga::front::glsl::Options::from(stage), &source).unwrap();
    let info = naga::valid::Validator::new(naga::valid::ValidationFlags::all(), naga::valid::Capabilities::all()).validate(&module).unwrap();
    let mut options=naga::back::spv::Options::default();
    // Rynix Mat4 already produces Vulkan clip coordinates (Y flipped, depth 0..1).
    options.flags.remove(naga::back::spv::WriterFlags::ADJUST_COORDINATE_SPACE);
    let words = naga::back::spv::write_vec(&module,&info,&options,Some(&naga::back::spv::PipelineOptions { shader_stage:stage,entry_point:"main".into() })).unwrap();
    let n=words.len();
    let name=&args[2];
    let body=words.iter().map(|v|v.to_string()).collect::<Vec<_>>().join(", ");
    fs::write(&args[3],format!("#[repr(C)]\npub struct {name}Words {{ words: [u32; {n}] }}\npub fun shader() -> {name}Words => {name}Words {{ words: [{body}] }}\npub fun size() -> u64 => {}\n// {name}\n",n*4)).unwrap();
}
