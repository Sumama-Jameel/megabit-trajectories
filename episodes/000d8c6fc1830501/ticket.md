# Cannot add custom emoji codes

## What happens now
Users can only use a fixed set of emoji codes that are built into the library. When someone tries to use an emoji code that is not in the predefined list, it does not work and shows an error instead.

## What should happen
Users should be able to add their own emoji codes to the library. This means they can define new emoji shortcodes and use them in their text, just like the built-in ones.

## About this project
This project is a Python library for rich text and beautiful formatting in the terminal. It provides features like colored text, tables, progress bars, and emoji support to make command-line applications more visually appealing and user-friendly.

## Problem this solves
People need to use special or custom emoji that are not included in the standard set. Without this, they cannot represent their brand, special symbols, or unique icons in terminal output.

## What changed
The library now lets users add their own emoji codes. They can define new emoji shortcodes and the library will recognize and display them, just like the built-in emoji.

## Impact
This improves ease of use and flexibility for anyone who needs custom emoji in their terminal applications.

## User experience
Before: A user tries to use `:custom_icon:` in their text, but it appears as plain text or causes an error because the library does not recognize it.

After: The user adds their own emoji code for `:custom_icon:`, and when they use it in their text, it displays the correct emoji image in the terminal.

## Hints
- /workspace/rich/emoji.py
- /workspace/rich/_emoji_codes.py
- /workspace/rich/_emoji_replace.py
- /workspace/tests/test_emoji.py