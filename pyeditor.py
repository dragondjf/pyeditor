#!/usr/bin/env python

"""PyQt4 port of the richtext/syntaxhighlighter example from Qt v4.x"""

from PySide import QtCore, QtGui


class MainWindow(QtGui.QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setupFileMenu()
        self.setupHelpMenu()
        self.setupEditor()

        self.setCentralWidget(self.editor)
        self.setWindowTitle("Syntax Highlighter")

    def about(self):
        QtGui.QMessageBox.about(self, "About Syntax Highlighter",
                                "<p>The <b>Syntax Highlighter</b> example shows how to "
                                "perform simple syntax highlighting by subclassing the "
                                "QSyntaxHighlighter class and describing highlighting "
                                "rules using regular expressions.</p>")

    def newFile(self):
        self.editor.clear()

    def openFile(self, path=None):
        if not path:
            path = QtGui.QFileDialog.getOpenFileName(self, "Open File",
                                                     '', "C++ Files (*.py *.pyw)")

        if path:
            inFile = QtCore.QFile(path[0])
            if inFile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
                text = inFile.readAll()

                try:
                    # Python v3.
                    text = str(text, encoding='ascii')
                except TypeError:
                    # Python v2.
                    text = str(text)

                self.editor.setPlainText(text)

    def setupEditor(self):
        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)

        self.editor = PyTextEdit()
        self.editor.setFont(font)

        self.highlighter = PythonHighlighter(self.editor.document())
        self.connect(self.editor.document(), QtCore.SIGNAL("contentsChange(int, int, int)"), self.highlighter.highlight)

    def setupFileMenu(self):
        fileMenu = QtGui.QMenu("&File", self)
        self.menuBar().addMenu(fileMenu)

        fileMenu.addAction("&New...", self.newFile, "Ctrl+N")
        fileMenu.addAction("&Open...", self.openFile, "Ctrl+O")
        fileMenu.addAction("E&xit", QtGui.qApp.quit, "Ctrl+Q")

    def setupHelpMenu(self):
        helpMenu = QtGui.QMenu("&Help", self)
        self.menuBar().addMenu(helpMenu)

        helpMenu.addAction("&About", self.about)
        helpMenu.addAction("About &Qt", QtGui.qApp.aboutQt)


class PyTextEdit(QtGui.QTextEdit):

    def __init__(self, parent=None):
        super(PyTextEdit, self).__init__(parent)

    def event(self, event):
        if event.type() == QtCore.QEvent.KeyPress and \
           event.key() == QtCore.Qt.Key_Tab:
            cursor = self.textCursor()
            cursor.insertText("    ")
            return True
        return super(PyTextEdit, self).event(event)


class PythonHighlighter(QtGui.QSyntaxHighlighter):

    Rules = []
    Formats = {}

    KEYWORDS = ["and", "as", "assert", "break", "class", "continue",
                "def", "del", "elif", "else", "except", "exec", "finally",
                "for", "from", "global", "if", "import", "in", "is", "lambda",
                "not", "or", "pass", "print", "raise", "return", "try",
                "while", "with", "yield"]

    BUILTINS = ["abs", "all", "any", "basestring", "bool", "callable",
                "chr", "classmethod", "cmp", "compile", "complex", "delattr",
                "dict", "dir", "divmod", "enumerate", "eval", "execfile",
                "exit", "file", "filter", "float", "frozenset", "getattr",
                "globals", "hasattr", "hex", "id", "int", "isinstance",
                "issubclass", "iter", "len", "list", "locals", "long", "map",
                "max", "min", "object", "oct", "open", "ord", "pow",
                "property", "range", "reduce", "repr", "reversed", "round",
                "set", "setattr", "slice", "sorted", "staticmethod", "str",
                "sum", "super", "tuple", "type", "unichr", "unicode", "vars",
                "xrange", "zip"]

    CONSTANTS = ["False", "True", "None", "NotImplemented", "Ellipsis"]

    def __init__(self, parent=None):
        super(PythonHighlighter, self).__init__(parent)
        self.initializeFormats()
        self.initializeRegExp()

    @staticmethod
    def initializeFormats():
        baseFormat = QtGui.QTextCharFormat()
        baseFormat.setFontFamily("courier")
        baseFormat.setFontPointSize(10)
        for name, color, bold, italic in (
                ("normal", "#000000", False, False),
                ("keyword", "#000080", True, False),
                ("builtin", "#0000A0", False, False),
                ("constant", "#0000C0", False, False),
                ("decorator", "#0000E0", False, False),
                ("comment", "#007F00", False, True),
                ("string", "#808000", False, False),
                ("number", "#924900", False, False),
                ("error", "#FF0000", False, False),
                ("pyqt", "#50621A", False, False)):
            format = QtGui.QTextCharFormat(baseFormat)
            format.setForeground(QtGui.QColor(color))
            if bold:
                format.setFontWeight(QtGui.QFont.Bold)
            format.setFontItalic(italic)
            PythonHighlighter.Formats[name] = format

    def initializeRegExp(self):
        PythonHighlighter.Rules.append((QtCore.QRegExp(
                "|".join([r"\b%s\b" % keyword \
                for keyword in PythonHighlighter.KEYWORDS])),
                self.Formats["keyword"]))
        PythonHighlighter.Rules.append((QtCore.QRegExp(
                "|".join([r"\b%s\b" % builtin \
                for builtin in PythonHighlighter.BUILTINS])),
                self.Formats["builtin"]))
        PythonHighlighter.Rules.append((QtCore.QRegExp(
                "|".join([r"\b%s\b" % constant \
                for constant in PythonHighlighter.CONSTANTS])),
                self.Formats["constant"]))
        PythonHighlighter.Rules.append((QtCore.QRegExp(
                r"\b[+-]?[0-9]+[lL]?\b"
                r"|\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b"
                r"|\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b"),
                self.Formats["number"]))
        PythonHighlighter.Rules.append((QtCore.QRegExp(
                r"\bPyQt4\b|\bQt?[A-Z][a-z]\w+\b"), self.Formats["pyqt"]))
        PythonHighlighter.Rules.append((QtCore.QRegExp(r"\b@\w+\b"), self.Formats["decorator"]))
        PythonHighlighter.Rules.append((QtCore.QRegExp(r"#.*"), self.Formats["comment"]))     
        stringRe = QtCore.QRegExp(r"""(?:'[^']*'|"[^"]*")""")
        stringRe.setMinimal(True)
        PythonHighlighter.Rules.append((stringRe, self.Formats["string"]))
        self.stringRe = QtCore.QRegExp(r"""(:?"["]".*"["]"|'''.*''')""")
        self.stringRe.setMinimal(True)
        PythonHighlighter.Rules.append((self.stringRe, self.Formats["string"]))
        self.tripleSingleRe = QtCore.QRegExp(r"""'''(?!")""")
        self.tripleDoubleRe = QtCore.QRegExp(r'''"""(?!')''')

    def highlightBlock(self, text):
        for expression, format in self.Rules:
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

    def highlight(self, position, removed, added):
        doc = self.sender()
        block = doc.findBlock(position)
        if not block.isValid():
            return
    
        if added > removed:
            endBlock = doc.findBlock(position + added)
        else:
            endBlock = block

        # while block.isValid() and not (endBlock < block):
        #     self.highlightBlock1(block)
        #     block = block.next()

    # def highlightBlock1(self, block):
    #     layout = block.layout()
    #     text = block.text()
    
    #     overrides = []

    #     for pattern in self.mappings:
    #         for m in re.finditer(pattern,text):
    #             range = QtGui.QTextLayout.FormatRange()
    #             s,e = m.span()
    #             range.start = s
    #             range.length = e-s
    #             range.format = self.mappings[pattern]
    #             overrides.append(range)
    
    #     layout.setAdditionalFormats(overrides)
    #     block.document().markContentsDirty(block.position(), block.length())

if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.resize(640, 512)
    window.show()
    sys.exit(app.exec_())
