valid_decrypted = '''
{
  "tx_id": "0f534ffc-9442-414c-b39f-a756b4adc6cb",
  "collection": {
    "exercise_sid": "hfjdskf"
  },
  "metadata": {
    "user_id": "789473423",
    "ru_ref": "12345678901A"
  }
}
'''

invalid_decrypted = '''
{
  "tx_id": "0f534ffc-9442-414c-b39f-a756b4adc6cb",
  "metadata": {
    "user_id": "789473423",
    "ru_ref": null
  }
}
'''

test_secret = "seB388LNHgxcuvAcg1pOV20_VR7uJWNGAznE0fOqKxg=".encode('ascii')

test_data = {
    'valid':
        '{"tx_id":"0f534ffc-9442-414c-b39f-a756b4adc6cb","collection":'
        '{"exercise_sid":"hfjdskf"},"metadata":{"user_id":"789473423","ru_ref":"12345678901A"}}',
    'invalid': '{"cats":"are nice"}',
    'missing_metadata': '{"tx_id":"0f534ffc-9442-414c-b39f-a756b4adc6cb","collection":{"exercise_sid":"hfjdskf"}}'
}
