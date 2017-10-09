# MATLAB to Dash Docset

Convert MATLAB Help Document to Docset for Dash.app to use.

![image](https://user-images.githubusercontent.com/13360124/31325840-2eed5f30-ac87-11e7-87fb-47c8ef459e33.png)


### How to Use?

1. Please use `Python3` and  `macOS`

2. Install the dependence.
  ```shell
  pip install -r requirements.txt
  ```

3. Run the Python Script. 
   ```shell
   python matlab2docset.py
   ```

4. The script will auto find the `MATLAB.app` which was installed in your computer and create the docset file in your `~/Downloads` directory. The size of the docset file will be limited in 1MB.

### Contact

Please post bugs and issues on [github](https://github.com/acbetter/matlab2docset/issues). Thank you!

### 中文简介

本程序可以把 `MATLAB.app `自带的帮助文档转换成 `Dash.app` 可以使用的文档。