import base64,unittest
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import patch
from PIL import Image
from briefing_art import generate,prompt_for

class CoverTests(unittest.TestCase):
    def saved(self):return {'report':{'headline':'에너지 가격의 파급','themes':[{'title':'유가와 수입물가','category':'매크로'}]}}
    def test_topic_controls_scene(self):
        self.assertIn('refinery',prompt_for(self.saved()))
    def test_visitor_cannot_call_image_api(self):
        with patch('admin_auth.is_admin',return_value=False),patch('briefing_art.OpenAI') as client:
            with self.assertRaises(PermissionError):generate('test',self.saved())
            client.assert_not_called()
    def test_generated_cover_is_storable_jpeg(self):
        data=BytesIO();Image.new('RGB',(1536,1024),'navy').save(data,format='JPEG')
        response=SimpleNamespace(data=[SimpleNamespace(b64_json=base64.b64encode(data.getvalue()).decode())])
        with patch('admin_auth.is_admin',return_value=True),patch('briefing_art.OpenAI') as client:
            client.return_value.images.generate.return_value=response
            art=generate('test',self.saved())
            self.assertLess(len(art['b64']),500000)
            self.assertEqual(art['mime'],'image/jpeg')
            client.return_value.images.generate.assert_called_once()
            self.assertEqual(client.return_value.images.generate.call_args.kwargs['n'],1)
if __name__=='__main__':unittest.main()
