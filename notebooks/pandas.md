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
import numpy as np
import pandas as pd

rename_columns = True

df = pd.DataFrame([
    ('Ch 1', 'S 1.1', 3.0, 4.0, 4, 2, np.datetime64('2018-10-11'), np.datetime64('NaT')),
    ('Ch 1', 'S 1.2', 3.0, 1.0, 4, 3, np.datetime64('2018-10-11'), np.datetime64('2018-10-11')),
    ('Ch 1', 'S 1.3', 3.0, 5.0, 4, 4, np.datetime64('2018-10-11'), np.datetime64('NaT')),
    ('Ch 2', 'S 2.1', 2.0, 2.0, 4, 3, np.datetime64('2018-10-09'), np.datetime64('2018-10-09')),
], columns=['chapter_title', 'section_title', 'chapter_mastery', 'section_mastery', 'chapter_responses', 'section_responses', 'chapter_last_response_at', 'section_last_response_at'])

book_chapters = df.loc[:, ['chapter_title', 'section_title', 'chapter_mastery', 'chapter_responses', 'chapter_last_response_at']].\
    groupby('chapter_title').first().reset_index()

df
```

```python
# Chapter summary
chapter_summary = book_chapters.drop(['section_title'], axis=1).\
    set_index('chapter_title')

mask = chapter_summary['chapter_last_response_at'].notnull()
chapter_summary.loc[mask, 'chapter_last_response_at'] = pd.to_datetime(
    chapter_summary[mask]['chapter_last_response_at']).dt.strftime('%Y-%m-%d %H:%M')
chapter_summary.loc[~mask, 'chapter_last_response_at'] = ''

if rename_columns:
    chapter_summary.rename(
        columns={'chapter_mastery': 'Mastery', 'chapter_responses': 'Attempts', 'chapter_last_response_at': 'Last practised'}, inplace=True)
    chapter_summary.index.names = ['Chapter']

chapter_summary
```

```python
# Section summary
section_summary = df.drop(['chapter_mastery', 'chapter_responses', 'chapter_last_response_at'], axis=1).\
    set_index(['chapter_title', 'section_title'])

mask = section_summary['section_last_response_at'].notnull()
section_summary.loc[mask, 'section_last_response_at'] = pd.to_datetime(
    section_summary[mask]['section_last_response_at']).dt.strftime('%Y-%m-%d %H:%M')
section_summary.loc[~mask, 'section_last_response_at'] = ''

if rename_columns:
    section_summary.rename(
        columns={'section_mastery': 'Mastery', 'section_responses': 'Attempts',
                 'section_last_response_at': 'Last practised'}, inplace=True)
    section_summary.index.names = ['Chapter', 'Section']

section_summary
```

```python
# Book summary
book_chapters.loc[:, 'section_title'] = ''

book_values = []
for name, group in df.groupby(['chapter_title']):
    idx = book_chapters.chapter_title.eq(name).idxmax()
    book_values.append(book_chapters.iloc[idx].values.tolist())
    book_values.extend(group.loc[:, ['chapter_title', 'section_title', 'section_mastery', 'section_responses', 'section_last_response_at']].values.tolist())

book_summary = pd.DataFrame(book_values, columns=['chapter_title', 'section_title', 'mastery', 'responses', 'last_response_at']).\
    set_index(['chapter_title', 'section_title'])

mask = book_summary['last_response_at'].notnull()
book_summary.loc[mask, 'last_response_at'] = pd.to_datetime(
    book_summary[mask]['last_response_at']).dt.strftime('%Y-%m-%d %H:%M')
book_summary.loc[~mask, 'last_response_at'] = ''

if rename_columns:
    book_summary.rename(columns={
        'mastery': 'Mastery', 'responses': 'Attempts', 'last_response_at': 'Last practised'}, inplace=True)
    book_summary.index.names = ['Chapter', 'Section']

book_summary
```

```python

```
