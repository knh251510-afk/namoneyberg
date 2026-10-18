# Theme artwork

Generated with the built-in image_gen tool, using each existing image as an edit target.

Prompt set: preserve the same composition, objects, camera, materials and crop; change only time of day and illumination. Home imagery: early morning counterpart to the existing night image. Brief category imagery: blue-hour night counterpart to the existing daylight image. No additional objects, text or logos. Network imagery: preserve node positions and Earth horizon while changing the ambient illumination.

Files: static/home-{reading,data,connections}-{light,dark}.jpg and static/brief-{macro,global,industry}-{light,dark}.jpg. Six original assets remain unchanged. All variants are optimized local JPEGs; switching modes performs no generation call. Theme preference is shared across pages within the current session, with light as the default. Colors for CSS and charts are defined in theme_tokens.py.


Home directory update: corporate analysis uses its own annual-report spread and calculator image; calendar uses its own desk calendar and analogue clock. Both were generated with the built-in image tool, then edited with the same strict composition-preserving night prompt. Paths: static/home-{corporate,calendar}-{light,dark}.jpg. The five home categories now use five distinct compositions. Home layout: one featured briefing and four equally sized 2x2 tool panels.
