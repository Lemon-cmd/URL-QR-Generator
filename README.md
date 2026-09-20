# QR code Generator for URL
This is a simple python script to generate a QR code given a designated url link. 
```bash
python qr_code.py https://arxiv.org/pdf/2604.26841 --color=green
```
There are a variety of colors that the user can choose. See the options by using `--help`
```bash
python qr_code.py --help

positional arguments:
  url                   The target URL or text to encode

optional arguments:
  -h, --help            show this help message and exit
  --color {red,black,green,blue,brown}, -c {red,black,green,blue,brown}
                        QR color (default: blue)
```
Here is an example:
```bash
python qr_code.py https://arxiv.org/pdf/2604.26841 --color=green
```
![image]()
