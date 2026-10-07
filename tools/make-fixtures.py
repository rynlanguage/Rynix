"""Original, deterministic PNG/glTF/GLB fixtures; Python stdlib only."""
from pathlib import Path
import struct,json,zlib
root=Path(__file__).resolve().parents[1]/'examples'/'fps_3d'/'assets'
root.mkdir(parents=True,exist_ok=True)
def chunk(kind,data):
    return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
raw=b''.join(b'\0'+bytes(v for x in range(64) for v in ((240,204,96,255) if (x//8+y//8)%2 else (43,68,82,255))) for y in range(64))
png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',64,64,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b'')
(root/'checker.png').write_bytes(png)
vertices=[];indices=[]
faces=[((0,0,1),(1,0,0),(0,1,0)),((0,0,-1),(-1,0,0),(0,1,0)),((1,0,0),(0,0,-1),(0,1,0)),((-1,0,0),(0,0,1),(0,1,0)),((0,1,0),(1,0,0),(0,0,-1)),((0,-1,0),(1,0,0),(0,0,1))]
for fi,(n,r,u) in enumerate(faces):
    for a,b in [(0,0),(1,0),(1,1),(0,1)]:
        p=[n[k]*.5+r[k]*(a-.5)+u[k]*(b-.5) for k in range(3)]
        vertices.append(struct.pack('<8f',*p,*n,a,b))
    indices.extend(fi*4+i for i in [0,1,2,0,2,3])
binary=b''.join(vertices)+struct.pack('<36H',*indices)
metadata={'asset':{'version':'2.0'},'buffers':[{'uri':'crate.bin','byteLength':len(binary)}],'bufferViews':[{'buffer':0,'byteOffset':0,'byteLength':768,'byteStride':32},{'buffer':0,'byteOffset':768,'byteLength':72}], 'accessors':[{'bufferView':0,'byteOffset':0,'componentType':5126,'count':24,'type':'VEC3','min':[-.5,-.5,-.5],'max':[.5,.5,.5]},{'bufferView':0,'byteOffset':12,'componentType':5126,'count':24,'type':'VEC3'},{'bufferView':0,'byteOffset':24,'componentType':5126,'count':24,'type':'VEC2'},{'bufferView':1,'componentType':5123,'count':36,'type':'SCALAR'}], 'meshes':[{'primitives':[{'attributes':{'POSITION':0,'NORMAL':1,'TEXCOORD_0':2},'indices':3,'material':0}]}], 'materials':[{'pbrMetallicRoughness':{'baseColorFactor':[1,1,1,1],'baseColorTexture':{'index':0},'metallicFactor':0,'roughnessFactor':.7}}],'textures':[{'source':0}],'images':[{'uri':'checker.png'}],'nodes':[{'mesh':0}],'scenes':[{'nodes':[0]}],'scene':0}
(root/'crate.bin').write_bytes(binary)
(root/'crate.gltf').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
metadata['buffers'][0].pop('uri');metadata['buffers'][0]['byteLength']=len(binary)+len(png)
metadata['bufferViews'].append({'buffer':0,'byteOffset':len(binary),'byteLength':len(png)})
metadata['images']=[{'bufferView':2,'mimeType':'image/png'}]
j=json.dumps(metadata,separators=(',',':')).encode();j+=b' '*((-len(j))%4)
b=binary+png;b+=b'\0'*((-len(b))%4)
glb=struct.pack('<III',0x46546c67,2,12+8+len(j)+8+len(b))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(b),0x004e4942)+b
(root/'crate.glb').write_bytes(glb);(root/'truncated.glb').write_bytes(glb[:40])
metadata['accessors'][0]['byteOffset']=900000;metadata['buffers'][0]['uri']='crate.bin'
metadata['buffers'][0]['byteLength']=len(binary);metadata['images']=[{'uri':'checker.png'}]
(root/'invalid.gltf').write_text(json.dumps(metadata),encoding='utf-8')
