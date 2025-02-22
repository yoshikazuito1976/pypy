from flask import Flask, request, render_template_string
from werkzeug.utils import secure_filename
from PIL import Image
import magic
import os

app = Flask(__name__)

# アップロード先のディレクトリ（適宜変更してください）
UPLOAD_FOLDER = '/home/siwuser/flaskproject/flask/testproject/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 最大16MBまで

def allowed_file(filename):
    # ファイル名に拡張子が含まれ、かつ許可リスト内の拡張子かをチェック
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_mime(file_stream):
    """
    python-magic を使い、ファイルの先頭部分から MIME タイプを取得してチェックします。
    """
    file_stream.seek(0)  # ファイルポインタを先頭に戻す
    mime = magic.from_buffer(file_stream.read(1024), mime=True)
    file_stream.seek(0)  # 再度先頭に戻す
    return mime in ['image/png', 'image/jpeg', 'image/gif']

def is_valid_image(file_stream):
    """
    Pillow を用いて、画像として正しく読み込めるか、整合性に問題がないかをチェックします。
    """
    try:
        img = Image.open(file_stream)
        img.verify()  # 画像データが破損していないかを検証
    except Exception:
        return False
    return True



@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'ファイルが見つかりません'
        file = request.files['file']
        if file.filename == '':
            return 'ファイルが選択されていません'
        if file and allowed_file(file.filename):
            # MIME タイプの検証
            if not is_valid_mime(file.stream):
                return '不正なMIMEタイプです'
            # 画像としての整合性検証
            if not is_valid_image(file.stream):
                return '画像として読み込めません'
            # 検証後はファイルストリームのポインタを先頭に戻す必要があります
            file.stream.seek(0)
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return 'アップロード成功'
        else:
            return '許可されていないファイル形式です'
    return render_template_string('''
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>画像アップロード</title>
      </head>
      <body>
        <h1>画像アップロード</h1>
        <form method="post" enctype="multipart/form-data">
          <input type="file" name="file">
          <input type="submit" value="アップロード">
        </form>
      </body>
    </html>
    ''')

if __name__ == '__main__':
    # デバッグモードで実行（本番環境では適切な設定に変更してください）
    app.run(debug=True)