"""Generate the initial canonical catalog; never overwrite customized titles."""
import json, pathlib, unicodedata
ROOT = pathlib.Path(__file__).resolve().parents[1]
NAMES = 'El Gallo|El Diablito|La Dama|El Catrín|El Paraguas|La Sirena|La Escalera|La Botella|El Barril|El Árbol|El Melón|El Valiente|El Gorrito|La Muerte|La Pera|La Bandera|El Bandolón|El Violoncello|La Garza|El Pájaro|La Mano|La Bota|La Luna|El Cotorro|El Borracho|El Negrito|El Corazón|La Sandía|El Tambor|El Camarón|Las Jaras|El Músico|La Araña|El Soldado|La Estrella|El Cazo|El Mundo|El Apache|El Nopal|El Alacrán|La Rosa|La Calavera|La Campana|El Cantarito|El Venado|El Sol|La Corona|La Chalupa|El Pino|El Pescado|La Palma|La Maceta|El Arpa|La Rana'.split('|')
def slug(name):
    return ''.join(c for c in unicodedata.normalize('NFD', name.lower()) if unicodedata.category(c) != 'Mn').split(' ', 1)[-1].replace(' ', '-')
if __name__ == '__main__':
    target = ROOT / 'assets/loteria/manifest.json'
    if target.exists():
        raise SystemExit('Catalog already exists; edit it directly to preserve titles.')
    cards=[]
    for number,name in enumerate(NAMES,1):
        s=slug(name); base=f'{number:02}-{s}'
        cards.append(dict(id=number, number=number, name=name, title=name, slug=s,
            images=dict(pixel=f'images/pixel/{base}.png', traditional=f'images/traditional/{base}.jpg'),
            audio={'repo':f'audio/repo/{base}.m4a','loteriacard':f'audio/loteriacard/{base}.mp3',**{v:f'audio/{v}/{base}.mp3' for v in ('generated-es','generated-en','generated-verses-es')}}))
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(cards,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
