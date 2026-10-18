"""Shared semantic colors for CSS, charts and theme-aware artwork."""
LIGHT={'bg':'#ffffff','surface':'#f7f9f9','soft':'#eef1f4','hover':'#e9edf2','border':'#dfe4e9','text':'#202927','muted':'#65716c','accent':'#4a4a4a','on-accent':'#ffffff','accent-hover':'#303030','rise':'#c83345','fall':'#2365bd','grid':'#e8eeea'}
DARK={'bg':'#141414','surface':'#202020','soft':'#2b2b2b','hover':'#333333','border':'#3d3d3d','text':'#ededed','muted':'#b5b5b5','accent':'#d6d6d6','on-accent':'#171717','accent-hover':'#eeeeee','rise':'#ff8991','fall':'#83b7ff','grid':'#343434'}
PALETTES={'light':['#23705f','#386cb0','#8761a6','#b07924','#b45270','#30858c','#74802d','#687887'],'dark':['#97cdb7','#99bce8','#c1acf3','#e4be83','#e5a9bd','#80cad7','#bacd97','#b5c2cb']}
def colors(mode='light'):return dict(DARK if mode=='dark' else LIGHT)
def css(mode='light'):
    t=colors(mode)
    tokens={**{'--nb-'+k:v for k,v in t.items()},'color-scheme':mode,
        '--seed-color-bg-brand-solid':t['accent'],'--seed-color-bg-brand-solid-pressed':t['accent-hover'],
        '--seed-color-fg-on-brand-solid':t['on-accent'],'--seed-color-bg-brand-weak':t['soft'],
        '--seed-color-palette-carrot-300':t['border'],'--seed-color-palette-carrot-600':t['accent'],'--seed-color-palette-carrot-700':t['accent'],'--seed-color-palette-carrot-800':t['accent'],'--seed-color-fg-brand':t['accent'],'--seed-color-fg-neutral':t['text'],'--seed-color-fg-neutral-muted':t['muted']}
    return ':root{'+''.join(k+':'+v+';' for k,v in tokens.items())+'}'
