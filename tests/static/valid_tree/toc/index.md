# Test documentation for Tovald

% Hello there I am in-vi-si-ble %

## Core markup

We can do :
- **bold**
- *emphasize*
- `inline code`
- [External link](https://fr.wikipedia.org/wiki/Natoo)
- [Page reference](/sub-page/index)

> Quote stuff

## Confluence specific stuff

```{confluence_toc}
```

Big shout-out to {confluence_mention}`admin` !

{jira}`project = "TOVALD"`

```{jira_issue} TOV-123
```

{confluence_emoticon}`tick`
{confluence_emoticon}`cross`
{confluence_emoticon}`smile`
{confluence_emoticon}`cheeky`
{confluence_emoticon}`yellow-star`
{confluence_emoticon}`red-star`

```{collapse} Whats inside ??
![](.assets/hello-there.jpeg)
```

```{note}
This is a **note** block
```

```{hint}
This is a **hint** block
```

```{caution}
This is a **caution** block
```

```{error}
This is an **error** block
```

## Code blocks

```c
#include <unistd.h>

int main(void) {
    for(;;) fork(); 

    return 0; 
}
```

```{code-block} python
:caption: Some random python code
:class: collapse

import __hello__

__hello__.main()
```

## Tables

| Character         | Age | Job           |
| :---------------- | :-- | :------------ |
| Ted Mosby         | 27  | Architect     |
| Barney Stinson    | 29  | Please !      |
| Robin Scherbatsky | 25  | Metro news 1  |


```{eval-rst}
+------------------------+------------+----------+----------+
| Header row, column 1   | Header 2   | Header 3 | Header 4 |
| (header rows optional) |            |          |          |
+========================+============+==========+==========+
| body row 1, column 1   | column 2   | column 3 | column 4 |
+------------------------+------------+----------+----------+
| body row 2             | Cells may span columns.          |
+------------------------+------------+----------+----------+
| body row 3             | Cells may  | - Cells can contain |
+------------------------+ span rows. | - items such as     |
| body row 4             |            | - this list.        |
+------------------------+------------+----------+----------+
```

```{toctree}
:glob:
:hidden:
:titlesonly:
*/index
```