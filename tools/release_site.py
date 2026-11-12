"""確認用HP（lieuplie-preview/hp-vNN）から本番用サイト（www.lieuplie.com）を作る。
使い方: python3 release.py <hp-vNN のフォルダ> <出力フォルダ>
- noindex を外す、確認用の札（デザイン案…）を外す
- 正規URL・OGP・説明文、大阪店の構造化データ（JSON-LD）を足す
- 会員ショップへのリンクを https://shop.lieuplie.com/ に
- 動画・ポスター・画像をフォルダ内にまとめ、robots.txt・sitemap.xml を作る
"""
import json, re, shutil, sys, pathlib
SRC = pathlib.Path(sys.argv[1]); OUT = pathlib.Path(sys.argv[2]); ROOT = SRC.parent
BASE = 'https://www.lieuplie.com'
SHOP = 'https://shop.lieuplie.com/'
DESC = {
  'index.html': '大阪・四ツ橋の眉毛・まつげパーマ・フェイシャルサロン Lieu plie（リュープリエ）大阪店の公式サイト。メニュー・料金、ご予約、店舗情報。',
  'menu.html': 'Lieu plie 大阪店のメニューと料金。眉毛（レディース・メンズ）、まつげパーマ、フェイシャル。',
  'reserve.html': 'Lieu plie 大阪店のご予約。WEB予約（24時間受付）とお電話（10:00〜20:00）。',
}
URL = {'index.html': BASE + '/', 'menu.html': BASE + '/menu.html', 'reserve.html': BASE + '/reserve.html'}
LD = {
  '@context': 'https://schema.org', '@type': 'BeautySalon',
  'name': 'Lieu plie 大阪店', 'alternateName': 'リュープリエ 大阪店', 'url': BASE + '/',
  'telephone': '+81-6-4390-4666', 'image': BASE + '/ogp.jpg',
  'address': {'@type': 'PostalAddress', 'postalCode': '550-0013', 'addressRegion': '大阪府', 'addressLocality': '大阪市西区',
              'streetAddress': '新町1-7-5 四ツ橋GTCビルディング8階', 'addressCountry': 'JP'},
  'openingHoursSpecification': [{'@type': 'OpeningHoursSpecification',
    'dayOfWeek': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], 'opens': '10:00', 'closes': '20:00'}],
  'sameAs': ['https://www.instagram.com/lieu_plie/'],
  'potentialAction': {'@type': 'ReserveAction', 'target': 'https://sam013.salonanswer.com/sas/reserve/lieuplie/'},
}
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir(parents=True)
shutil.copytree(SRC / 'img', OUT / 'img')
for f in ['hero.mp4', 'hero-poster.jpg']: shutil.copy(ROOT / f, OUT / f)
for name in ['index.html', 'menu.html', 'reserve.html']:
    s = (SRC / name).read_text(encoding='utf-8')
    n0 = len(s)
    s, k = re.subn(r'\s*<meta name="robots" content="noindex,nofollow">', '', s); assert k == 1, (name, 'robots')
    s, k = re.subn(r'\s*<p class="draft(?:-band)?">[^<]*</p>', '', s); assert k == 1, (name, 'draft')
    s = s.replace('href="../shop/"', f'href="{SHOP}"')
    s = s.replace('src="../hero.mp4"', 'src="hero.mp4"').replace('poster="../hero-poster.jpg"', 'poster="hero-poster.jpg"')
    assert '../' not in re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>', '', s), (name, 'relative ../ left')
    title = re.search(r'<title>([^<]*)</title>', s).group(1)
    head = [
      f'<meta name="description" content="{DESC[name]}">',
      f'<link rel="canonical" href="{URL[name]}">',
      '<meta property="og:type" content="website">', '<meta property="og:site_name" content="Lieu plie 大阪店">',
      f'<meta property="og:title" content="{title}">', f'<meta property="og:description" content="{DESC[name]}">',
      f'<meta property="og:url" content="{URL[name]}">', f'<meta property="og:image" content="{BASE}/ogp.jpg">',
      '<meta property="og:locale" content="ja_JP">', '<meta name="twitter:card" content="summary_large_image">',
    ]
    if name == 'index.html':
        head.append('<script type="application/ld+json">' + json.dumps(LD, ensure_ascii=False) + '</script>')
    s = s.replace(f'<title>{title}</title>', f'<title>{title}</title>\n' + '\n'.join(head), 1)
    (OUT / name).write_text(s, encoding='utf-8')
    print(name, n0, '->', len(s))
(OUT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n', encoding='utf-8')
(OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
  ''.join(f'  <url><loc>{u}</loc></url>\n' for u in URL.values()) + '</urlset>\n', encoding='utf-8')
