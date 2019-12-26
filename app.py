from flask import Flask, render_template, session, request, redirect, url_for, flash
from flaskext.mysql import MySQL
import secrets
from datetime import date

generated_token = secrets.token_hex(16)
app = Flask(__name__)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'db_pegawai'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['SECRET_KEY'] = generated_token

mysql.init_app(app)

@app.route('/')
def main():
    if 'username' in session:
        return redirect('/profile')
    else:
        return render_template('index.html')

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        if 'username' in session:
            return redirect('profile')
        else:
            return render_template('login.html')
    else:
        user = request.form['username']
        password = request.form['password']
        cursor = mysql.connect().cursor()
        cursor.execute("SELECT * from tbl_user where username='" + user + "' and password='" + password + "'")
        data = cursor.fetchone()
        if data is None:
            flash("Username dan Password anda Salah")
            return redirect('login')
        else:
            session['username'] = user
            return redirect('profile')    

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        if 'username' in session:
            return redirect('profile')
        else:
            return render_template('register.html')
    else:
        user = request.form['username']
        password = request.form['password']
        rePass = request.form['rePass']
        cursor = mysql.connect().cursor()
        cursor.execute("SELECT * from tbl_user where username='" + user + "'")
        data = cursor.fetchone()
        if (password!=rePass):
            return "password dan konfirmasi password tidak sama"
        elif data is None:
            sql = "INSERT INTO `tbl_user` (`username`, `password`, `nama`, `tgl_lahir`, `jk`, `agama`, `kwgn`, `nama_ayah`, `nama_ibu`, `pekerjaan_ayah`, `pekerjaan_ibu`, `sekolah_asal`, `telp`, `alamat`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (user, password, '', '', '', '', '', '', '', '', '', '', '', ''))
            return redirect('login')
        else:
            return "user sudah terdaftar"

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('login')

@app.route('/cek_session')
def cek_session():
    if ('username' in session):
        return session['username']
    return "session kosong"

@app.route('/profile', methods=['POST', 'GET'])
def profile():
    if request.method == 'GET':
        if not 'username' in session:
            return redirect('login')
        else:
            user = session['username']
            cursor = mysql.connect().cursor()
            cursor.execute("SELECT * from tbl_user where username='" + user + "'")
            data = cursor.fetchone()
            print(data)
            return render_template('profile.html', data=data)
    else:
        user = request.form['username']
        nama = request.form['nama']
        tgl_lahir = request.form['tgl_lahir']
        jk = request.form['jk']
        agama = request.form['agama']
        kwgn = request.form['kwgn']
        nama_ayah = request.form['nama_ayah']
        nama_ibu = request.form['nama_ibu']
        pekerjaan_ayah = request.form['pekerjaan_ayah']
        pekerjaan_ibu = request.form['pekerjaan_ibu']
        sekolah_asal = request.form['sekolah_asal']
        telp = request.form['telp']
        alamat = request.form['alamat']

        cursor = mysql.connect().cursor()
        sql = "UPDATE tbl_user SET username=%s, nama=%s, tgl_lahir=%s, jk=%s, agama=%s, kwgn=%s, nama_ayah=%s, nama_ibu=%s, pekerjaan_ayah=%s, pekerjaan_ibu=%s, sekolah_asal=%s, telp=%s, alamat=%s WHERE username=%s"
        cursor.execute(sql, (user, nama, tgl_lahir, jk, agama, kwgn, nama_ayah, nama_ibu, pekerjaan_ayah, pekerjaan_ibu, sekolah_asal, telp, alamat, user))
        session['username'] = user

        return redirect('profile')

@app.route('/peraturan')
def peraturan():
    if 'username' in session:    
        id = request.args.get('id')
        cursor = mysql.connect().cursor()
        cursor.execute("SELECT * from tbl_peraturan where id=%s", (id))
        data = list(cursor.fetchone())
        if data[0]==7:
            data.append(url_for('static', filename='img/soalfa/{}'.format(data[5])))
        elif data[0]==8:
            data.append(url_for('static', filename='img/soalwu/{}'.format(data[5])))
        print(data)
        return render_template('peraturan.html', data=data)
    else:
        return redirect('login')

@app.route('/soal', methods=['GET', 'POST'])
def soal():
    if request.method == 'GET':
        # if 'username' in session:
        id = request.args.get('id')
        cursor = mysql.connect().cursor()
        cursor.execute("SELECT * from tabel_soal where id_soal=%s", (id))
        result = list(cursor.fetchall())
        cursor.execute("SELECT * from tbl_peraturan where id=%s", (id))
        result_peraturan = list(cursor.fetchone())
        data = []
        data.append(result)
        data.append(result_peraturan[2])
        data.append(int(id))
        print(data)
        return render_template('soal.html', data=data)
    elif request.method == 'POST':
        benar = 0
        salah = 0
        kosong = 0
        id_soal = request.form['id_soal']
        id_user = session['username']
        tanggal = date.today()
        cursor = mysql.connect().cursor()
        cursor.execute("SELECT * from tabel_soal where id_soal=%s", (id_soal))
        result = list(cursor.fetchall())
        for row in result:
            knc_jawaban = row[19]
            knc_jawaban2 = row[20]
            i = row[2]
            n = i
            if (id_soal=='1' or id_soal=='2' or id_soal=='3' or id_soal=='7' or id_soal=='8' or id_soal=='9' or id_soal=='10'):
                jawaban = request.form.get(i)
                print("hehe {}".format(jawaban))
                if jawaban:
                    if (knc_jawaban==jawaban):
                        benar+=1
                    else:
                        salah+=1
                else:
                    kosong+=1
            elif (id_soal=='4'):
                jawaban = request.form.get(i)
                if jawaban:
                    answer = jawaban.lower()
                    if (knc_jawaban == answer):
                        benar+=2
                    elif knc_jawaban2 == answer:
                        benar+=1
                    elif answer == '':
                        kosong+=1
                    else:
                        salah+=1
                else:
                    kosong+=1
            elif (id_soal == '5' or id_soal == '6'):
                print(request.form.getlist(i))
            print(benar)
            print(salah)
            print(kosong)
        return "test"

if __name__ == "__main__":
    app.run(debug=True)