================
Gigya Server Lib
================

**Notice: This work is not sponsored or otherwise acknowledged by Gigya Inc in any way shape or form.**

Gigya Server Lib (gslib) is a python adaptation of the `Gigya Server SDK <http://developers.gigya.com/030_Server_SDKs>`_ to python.


Typical Usage
=============

Properly initialized, gslib is very simple to use::
    # Make a request to gigya (retrieve a user's data from GCS)
    gslib.Request('gcs.getUserData',
                  params={"UID": '<user UID>, "fields": "*"},
                  use_https=True).send()
    
    # Verify an event's signature (gigya_dict contains a json response 
    # loaded to a dict with json.loads)
    # See: http://bit.ly/NZ2Bpc
    gslib.SigUtils.signature_validate(gigya_dict['signatureTimestamp'],
                                        gigya_dict['UID'],
                                        gigya_dict['UIDSignature'])


Initialization
--------------

If used inside a django application gslib will automatically look for the following settings::

    settings.GIGYA_API_KEY
    settings.GIGYA_SECRET_KEY

If used inside a flask application, initialization can be done by calling ``gslib.initialize_app``, gslib will expect similar keys on the flask app's config (``GIGYA_API_KEY`` and ``GIGYA_SECRET_KEY``).

Otherwise the api key and secret key can be sent as arguments to the constructor of a ``Request``.