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
            session['iduser'] = data[0]
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
    session.pop('iduser', None)
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

@app.route('/peraturan', methods=['GET', 'POST'])
def peraturan():
    if request.method=='GET':
        if 'username' in session:    
            id = request.args.get('id')
            cursor = mysql.connect().cursor()
            cursor.execute("SELECT * from tbl_peraturan where id=%s", (id))
            data = [list(cursor.fetchone()), id]
            if data[0][0]==7:
                data.append(url_for('static', filename='img/soalfa/{}'.format(data[0][5])))
            elif data[0][0]==8:
                data.append(url_for('static', filename='img/soalwu/{}'.format(data[0][5])))
            print(data)
            return render_template('peraturan.html', data=data)
        else:
            return redirect('login')
    else:
        id = request.form['id']
        print(id)
        return redirect(url_for('soal', id=id))
        # return redirect("soal?id=".format(id))
        # return "test"

@app.route('/soal', methods=['GET', 'POST'])
def soal():
    if request.method == 'GET':
        if 'username' in session:
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
        else:
            return redirect('login')
    elif request.method == 'POST':
        benar = 0
        salah = 0
        kosong = 0
        id_soal = request.form['id_soal']
        id_user = session['iduser']
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
                if "{}".format(i) in request.form:
                    jawaban = request.form["{}".format(i)]
                    # if jawaban:
                    if (knc_jawaban==jawaban):
                        benar+=1
                    else:
                        salah+=1
                else:
                    kosong+=1
            elif (id_soal=='4'):
                if "{}".format(i) in request.form:
                    jawaban = request.form["{}".format(i)]
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
                if "{}".format(i) in request.form:
                    s = ""
                    jawaban = s.join(request.form.getlist("{}".format(i)))
                    if (jawaban==knc_jawaban or jawaban==knc_jawaban2):
                        benar+=1
                    else:
                        salah+=1
                else:
                    kosong+=1
        score = benar
        keterangan = ""
        if (score>=10):
            keterangan = "Rata-rata"
        else:
            keterangan = "Dibawah Rata-rata"
        sql = "INSERT INTO `tbl_nilai` (`id_user`, `id_soal`, `benar`, `salah`, `kosong`, `score`, `tanggal`, `keterangan`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (id_user, id_soal, benar, salah, kosong, score, tanggal, keterangan))
        newId = int(id_soal) + 1
        if (newId<=10):
            return redirect(url_for("peraturan", id=newId))
        else:
            return redirect("nilai")

@app.route('/nilai', methods=['GET', 'POST'])
def nilai():
    if request.method=='GET':
        if 'username' in session:
            user = session['username']
            iduser = session['iduser']
            tanggal = date.today()
            cursor = mysql.connect().cursor()
            print(iduser)
            print(tanggal)
            cursor.execute("SELECT * from tbl_nilai WHERE id_user=%s ORDER BY id_soal ASC", (iduser))
            result = list(cursor.fetchall())
            total = sum([int(r[6]) for r in result])
            iq = 0
            if (total>138 and total<=140):
                iq = 160
            elif (total>136 and total<=138):
                iq = 157
            elif (total>134 and total<=136):
                iq = 154
            elif (total>132 and total<=134):
                iq = 151
            elif (total>129 and total<=132):
                iq = 145
            elif (total>128 and total<=129):
                iq = 143
            elif (total>127 and total<=128):
                iq = 142
            elif (total>126 and total<=127):
                iq = 140
            elif (total>125 and total<=126):
                iq = 139
            elif (total>124 and total<=125):
                iq = 137
            elif (total>123 and total<=124):
                iq = 136
            elif (total>122 and total<=123):
                iq = 134
            elif (total>121 and total<=122):
                iq = 133
            elif (total>120 and total<=121):
                iq = 131
            elif (total>119 and total<=120):
                iq = 130
            elif (total>118 and total<=119):
                iq = 128
            elif (total>117 and total<=118):
                iq = 127
            elif (total>116 and total<=117):
                iq = 125
            elif (total>115 and total<=116):
                iq = 124
            elif (total>114 and total<=115):
                iq = 122
            elif (total>113 and total<=114):
                iq = 121
            elif (total>112 and total<=113):
                iq = 120
            elif (total>111 and total<=112):
                iq = 118
            elif (total>110 and total<=111):
                iq = 116
            elif (total>109 and total<=110):
                iq = 115
            elif (total>108 and total<=109):
                iq = 113
            elif (total>107 and total<=108):
                iq = 112
            elif (total>106 and total<=107):
                iq = 110
            elif (total>105 and total<=106):
                iq = 109
            elif (total>104 and total<=105):
                iq = 107
            elif (total>103 and total<=104):
                iq = 106
            elif (total>102 and total<=103):
                iq = 104
            elif (total>101 and total<=102):
                iq = 103
            elif (total>100 and total<=101):
                iq = 101
            elif (total>99 and total<=100):
                iq = 100
            elif (total>98 and total<=99):
                iq = 98
            elif (total>97 and total<=98):
                iq = 97
            elif (total>96 and total<=97):
                iq = 96
            elif (total>95 and total<=96):
                iq = 94
            elif (total>94 and total<=95):
                iq = 92
            elif (total>93 and total<=94):
                iq = 91
            elif (total>92 and total<=93):
                iq = 90
            elif (total>91 and total<=92):
                iq = 88
            elif (total>90 and total<=91):
                iq = 87
            elif (total>89 and total<=90):
                iq = 85
            elif (total>88 and total<=89):
                iq = 84
            elif (total>87 and total<=88):
                iq = 82
            elif (total>86 and total<=87):
                iq = 81
            elif (total>85 and total<=86):
                iq = 79
            elif (total>84 and total<=85):
                iq = 78
            elif (total>83 and total<=84):
                iq = 76
            elif (total>82 and total<=83):
                iq = 75
            elif (total>81 and total<=82):
                iq = 73
            elif (total>80 and total<=81):
                iq = 71
            elif (total>79 and total<=80):
                iq = 70
            elif (total>78 and total<=79):
                iq = 68
            elif (total>77 and total<=78):
                iq = 67
            elif (total>76 and total<=77):
                iq = 66
            elif (total>75 and total<=76):
                iq = 64
            elif (total>74 and total<=75):
                iq = 62
            elif (total>73 and total<=74):
                iq = 61
            elif (total>72 and total<=73):
                iq = 59
            elif (total>70 and total<=72):
                iq = 58
            elif (total>68 and total<=70):
                iq = 55
            elif (total>66 and total<=68):
                iq = 52
            elif (total>64 and total<=66):
                iq = 49
            elif (total>62 and total<=64):
                iq = 46
            elif (total>60 and total<=62):
                iq = 43
            elif (total>58 and total<=60):
                iq = 40
            elif (total<=60):
                iq = 37
            
            status = ""

            if (iq>=140):
                status = "Very Superior"
            elif (iq>=120 and iq<=139):
                status = "Superior"
            elif (iq>=110 and iq<=119):
                status = "High Average"
            elif (iq>=100 and iq<=109):
                status = "Normal or Average"
            elif (iq>=80 and iq<=99):
                status = "Low Average"
            elif (iq>=60 and iq<=79):
                status = "Borderline Defective"
            elif (iq>=30 and iq<=59):
                status = "Borderline Defective"
            
            data = [result, total, iq, status]
            print(data)
            return render_template('nilai.html', data=data)
        else:
            return redirect('login')

if __name__ == "__main__":
    app.run(debug=True)