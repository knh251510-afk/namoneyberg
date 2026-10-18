"""Shared semantic colors for CSS, charts and theme-aware artwork."""
LIGHT={'bg':'#ffffff','surface':'#f7f9f9','soft':'#edf4f1','hover':'#f1f4f2','border':'#e2e8e5','text':'#202927','muted':'#65716c','accent':'#23705f','on-accent':'#ffffff','accent-hover':'#195244','rise':'#c83345','fall':'#2365bd','grid':'#e8eeea'}
DARK={'bg':'#10171b','surface':'#182329','soft':'#22332f','hover':'#263832','border':'#34463f','text':'#e8f0ec','muted':'#a8b9b0','accent':'#97cdb7','on-accent':'#10231b','accent-hover':'#b6dfcb','rise':'#ff8991','fall':'#83b7ff','grid':'#2b3c35'}
PALETTES={'light':['#23705f','#386cb0','#8761a6','#b07924','#b45270','#30858c','#74802d','#687887'],'dark':['#97cdb7','#99bce8','#c1acf3','#e4be83','#e5a9bd','#80cad7','#bacd97','#b5c2cb']}
def colors(mode='light'):return dict(DARK if mode=='dark' else LIGHT)
def css(mode='light'):
    t=colors(mode)
    tokens={**{'--nb-'+k:v for k,v in t.items()},'color-scheme':mode,
        '--seed-color-bg-brand-solid':t['accent'],'--seed-color-bg-brand-solid-pressed':t['accent-hover'],
        '--seed-color-fg-on-brand-solid':t['on-accent'],'--seed-color-bg-brand-weak':t['soft'],
        '--seed-color-palette-carrot-300':t['border'],'--seed-color-palette-carrot-600':t['accent'],'--seed-color-palette-carrot-700':t['accent'],'--seed-color-palette-carrot-800':t['accent'],'--seed-color-fg-brand':t['accent'],'--seed-color-fg-neutral':t['text'],'--seed-color-fg-neutral-muted':t['muted']}
    return ':root{'+''.join(k+':'+v+';' for k,v in tokens.items())+'}'
