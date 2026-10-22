# Light theme

Current source of truth: `theme_tokens.py` (`LIGHT`) and the overrides in `assets/app-theme.css`.

| Role | Current token |
| --- | --- |
| Background | `#ffffff` |
| Surface | `#f7f9f9` |
| Main text | `#202927` |
| Secondary text | `#65716c` |
| Accent | `#4a4a4a` |
| Selected surface | `#eef1f4` |

These values supersede the earlier teal/brown/orange directions. Chart series retain their own categorical palette; price rise/fall semantics are separate from action accents. Theme switching shares tokens with charts. Test actual component states and mobile layout when changing styles.
