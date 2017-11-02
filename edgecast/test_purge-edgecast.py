import unittest
import os.path

event = {
      "Records": [
        {
          "eventVersion": "2.0",
          "eventTime": "1970-01-01T00:00:00.000Z",
          "requestParameters": {
            "sourceIPAddress": "127.0.0.1"
          },
          "s3": {
            "configurationId": "testConfigRule",
            "object": {
              "eTag": "0123456789abcdef0123456789abcdef",
              "sequencer": "0A1B2C3D4E5F678901",
              "key": "HappyFace.jpg",
              "size": 1024
            },
            "bucket": {
              "arn": "arn:aws:s3:::mybucket",
              "name": "mybucket",
              "ownerIdentity": {
                "principalId": "EXAMPLE"
              }
            },
            "s3SchemaVersion": "1.0"
          },
          "responseElements": {
            "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH",
            "x-amz-request-id": "EXAMPLE123456789"
          },
          "awsRegion": "us-east-1",
          "eventName": "ObjectCreated:Put",
          "userIdentity": {
            "principalId": "EXAMPLE"
          },
          "eventSource": "aws:s3"
        }
      ]
    }

    

class CDNTestCase(unittest.TestCase):
    """Tests for `purge-cdn.py`."""

    def test_is_akamai_working(self):
        """Is CDN receiving a successful purge?"""
        self.assertTrue(func(event))

    
if __name__ == '__main__': 

    module_name = 'purge-edgecast'
    exec_function = 'main'

    assert 'module_name' in locals(), 'Module name not supplied'
    assert 'exec_function' in locals(), 'Function name not supplied'
    assert os.path.isfile('{}.py'.format(module_name)), "File {} not found".format(module_name)

    module = __import__(module_name)
                
    func=getattr(module, exec_function)

    # print(func(event) ) 
    unittest.main()

