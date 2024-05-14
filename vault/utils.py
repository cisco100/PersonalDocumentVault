import qrcode
from stegano import lsb


def generate_qrcode(output_path,data=None,colors=[None,None]):
	qr = qrcode.QRCode(
	    version=1,
	    error_correction=qrcode.constants.ERROR_CORRECT_L,
	    box_size=10,
	    border=4,
	)
	qr.add_data(str(data))
	qr.make(fit=True)

	img = qr.make_image(fill_color=str(colors[0]), back_color=str(colors[1]))

	return img.save(str(output_path))



def conceal(key,output,img=generate_code("","",[,])):
	secret=lsb.hide(img,key)
	return secret.save(str(output)