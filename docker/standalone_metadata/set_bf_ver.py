"""\
Read the BF version from the BF pom and set bio-formats.version
accordingly in the pydoop-features pom.
"""
import xml.dom.minidom as dom
import re


def gettext(node):
    return "".join(
        c.data.strip() for c in node.childNodes if c.nodeType == c.TEXT_NODE
    )


def main():
    doc = dom.parse("bioformats/pom.xml")
    bf_ver = [gettext(_) for _ in doc.documentElement.childNodes
              if _.nodeName == "version"][0]
    with open("pydoop-features/pom.xml") as f:
        lines = [_ for _ in f]
    pattern = re.compile(r'^(\s*<bio-formats\.version>)([^<]+)(<.*)$')
    with open("pydoop-features/pom.xml", "w") as f:
        for l in lines:
            m = pattern.match(l)
            if m is None:
                f.write(l)
            else:
                groups = list(m.groups())
                groups[1] = bf_ver
                f.write("%s%s%s\n" % tuple(groups))


if __name__ == "__main__":
    main()
