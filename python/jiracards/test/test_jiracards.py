import unittest
from unittest.mock import call, Mock
from pathlib import Path
from reportlab.pdfgen.canvas import Canvas
from jiracards import jiracards


__location__ = Path(__file__).parent


class TestJiracards(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_draw_text(self):
        canvas = Canvas

        canvas.setFont = Mock()
        canvas.drawString = Mock()
        canvas.drawRightString = Mock()
        canvas.drawCentredString = Mock()
        canvas.stringWidth = Mock()
        canvas.stringWidth.return_value = 0
        canvas.saveState = Mock()
        canvas.restoreState = Mock()

        text = [
            {
                'text': ['Epic: ', 'abc'],
                'size': 6,
                'x': 10,
                'y': 10,
                'style': 'epic'
            },
            {
                'text': 'def',
                'size': 8,
                'x': 100,
                'y': 100,
                'align': 'right'
            },
            {
                'text': '123',
                'size': 10,
                'x': 1000,
                'y': 1000,
                'align': 'centered'
            }
        ]

        jiracards.draw_text(canvas, text)

        expected = [
            call("Helvetica", text[0]['size']),
            call("Helvetica", text[1]['size']),
            call("Helvetica", text[2]['size'])
        ]
        self.assertEquals(canvas.setFont.mock_calls, expected)

        expected = [
            call(text[0]['x'], text[0]['y'], text[0]['text'][0]),
            call(text[0]['x'], text[0]['y'], text[0]['text'][1])
        ]
        self.assertEquals(canvas.drawString.mock_calls, expected)

        expected = [
            call(text[1]['x'], text[1]['y'], text[1]['text'])
        ]
        self.assertEquals(canvas.drawRightString.mock_calls, expected)

        expected = [
            call(text[2]['x'], text[2]['y'], text[2]['text'])
        ]
        self.assertEquals(canvas.drawCentredString.mock_calls, expected)


if __name__ == '__main__':
    unittest.main()
