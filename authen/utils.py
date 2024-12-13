import uuid

def secretcode():
	uid=str(uuid.uuid4())
	SECRETCODE=uid[:12]
	return SECRETCODE

