---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.0'
      jupytext_version: 0.8.5
  kernelspec:
    display_name: Python 2
    language: python
    name: python2
  language_info:
    codemirror_mode:
      name: ipython
      version: 2
    file_extension: .py
    mimetype: text/x-python
    name: python
    nbconvert_exporter: python
    pygments_lexer: ipython2
    version: 2.7.12
---

```python
import pandas as pd

df = pd.DataFrame([
    ('Ch 1', 'S 1.1', 3.0, 4.0, 4, 2),
    ('Ch 1', 'S 1.2', 3.0, 1.0, 4, 3),
    ('Ch 1', 'S 1.3', 3.0, 5.0, 4, 4),
    ('Ch 2', 'S 2.1', 2.0, 2.0, 4, 3),
], columns=['chapter_title', 'section_title', 'chapter_mastery', 'section_mastery', 'chapter_attempts', 'section_attempts'])

chapter_df = df.loc[:, ['chapter_title', 'section_title', 'chapter_mastery', 'chapter_attempts']]
chapter_df = chapter_df.rename(columns={'chapter_mastery': 'mastery', 'chapter_attempts': 'attempts'})
chapter_df = chapter_df.groupby('chapter_title').first().reset_index()
chapter_df.loc[:, 'section_title'] = ''

rows = []
for name, group in df.groupby(['chapter_title']):
    idx = chapter_df.chapter_title.eq(name).idxmax()
    rows.append(chapter_df.iloc[idx].values.tolist())
    rows.extend(group.loc[:, ['chapter_title', 'section_title', 'section_mastery', 'section_attempts']].values.tolist())

book_df = pd.DataFrame(rows, columns=['chapter_title', 'section_title', 'mastery', 'attempts'])
book_df = book_df.set_index(['chapter_title', 'section_title'])
book_df
```
