"""Fetch entries from the official public ZIP using standard HTTP range requests."""
import io,json,zipfile,sys,subprocess,concurrent.futures
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
DEST=ROOT/'assets/spring-source'
URL='https://studio.blender.org/download-source/files/1b/1bffff08b464375d842e7da43b4f5293/1bffff08b464375d842e7da43b4f5293.zip'
SIZE=426238965
class Remote(io.RawIOBase):
    def __init__(self):self.pos=0
    def seekable(self):return True
    def readable(self):return True
    def tell(self):return self.pos
    def seek(self,offset,whence=0):
        self.pos=offset if whence==0 else self.pos+offset if whence==1 else SIZE+offset
        return self.pos
    def read(self,n=-1):
        if n<0:n=SIZE-self.pos
        n=min(n,SIZE-self.pos)
        if n<=0:return b''
        def fetch(start,length):
            return subprocess.run(['curl.exe','-L','--fail','--silent','--show-error','--retry','2','--range',f'{start}-{start+length-1}','--max-filesize',str(length),'--max-time','90',URL],capture_output=True,check=True).stdout
        if n>4*1024*1024:
            step=4*1024*1024
            ranges=[(self.pos+i,min(step,n-i)) for i in range(0,n,step)]
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
                data=b''.join(pool.map(lambda r:fetch(*r),ranges))
        else:data=fetch(self.pos,n)
        if len(data)!=n:raise RuntimeError('Unexpected HTTP range length')
        self.pos+=len(data);return data
with zipfile.ZipFile(Remote()) as z:
    infos=[{'name':i.filename,'bytes':i.file_size,'compressed':i.compress_size,'offset':i.header_offset} for i in z.infolist()]
    (DEST/'archive-contents.json').write_text(json.dumps(infos,indent=2))
    for i in infos:print(json.dumps(i),flush=True)
    if '--extract' in sys.argv:
        names=sys.argv[sys.argv.index('--extract')+1:]
        for name in names:
            target=(DEST/name).resolve()
            if not target.is_relative_to(DEST.resolve()):raise RuntimeError('Archive path outside source directory')
            target.parent.mkdir(parents=True,exist_ok=True)
            if target.exists() and target.stat().st_size==z.getinfo(name).file_size:continue
            print('FETCH',name,flush=True)
            target.write_bytes(z.read(name))
            print('SAVED',name,flush=True)
