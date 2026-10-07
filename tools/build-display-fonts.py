# Rebuild with Python + fonttools[woff]. Sources and OFL license are in fonts/.
# Pins Handjet axes and merges subsets to avoid partial-font rendering.
from pathlib import Path
from tempfile import TemporaryDirectory
scratch = TemporaryDirectory(prefix='embra-fonts-')
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.merge import Merger
root=Path(__file__).resolve().parents[1] / 'fonts'
for weight in [480,560]:
 paths=[]
 for subset in ['latin','latin-ext','vietnamese']:
  f=TTFont(root/f'Handjet-normal-100-900-{subset}.woff2')
  f=instantiateVariableFont(f,{'wght':weight,'ELGR':1,'ELSH':2},inplace=True)
  f.flavor=None
  p=str(Path(scratch.name) / f'{weight}-{subset}.ttf');f.save(p);paths.append(p)
 merged=Merger().merge(paths)
 merged.flavor='woff2';merged.save(root/f'Handjet-static-{weight}-v1.woff2')
 assert 'fvar' not in merged
 text='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789Mỗi lần deploy đều có đường lui. TỪ CODE ĐẾN APP. CÙNG EMBRA. ăâđêôơưĂÂĐÊÔƠƯ'
 assert all(ord(c) in merged.getBestCmap() for c in text)
 print(weight,'static font',len(merged.getBestCmap()),'characters verified')
