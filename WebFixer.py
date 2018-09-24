from  flask import Flask
from flask import make_response, request, Response
import ScheduleFixer.Fixer as fixer

app = Flask(__name__)

@app.route('/')
def form():
    return """
        <html>
            <body>
                <h1>HUJI medicine schedule fixer</h1>
                First, get your schedule file from the rishum-net. This is an *.ics file. You can find it when rishum is active:
                <br>
                <img src="static/cal_tut_1.png">
                <br>
                <img src="static/cal_tut_2.png">
                <br>
                Just save the file, don't open it (Windows will try to open it automatically using Outlook).
                <br>
                <form action="/fixSchedule" method="post" enctype="multipart/form-data">
                    Now, upload the *.ics file here: <input type="file" name="data_file" />
                    <br>
                    Enter the school year (E.g., for 2018-19, write 2019) <input type="string" name="year" /> 
                    <br>
                    Use Hadassah-style (xx:15) start times? <input type="checkbox" name="hadassah_start_times"/> 
                    <br>
                    <input type="submit" value="Fix"/>
                </form>
                <br>
                Now, import the new "fixed_schedule.ics" file to your favorite calendar. 
                For example, if you're using Google Calendar (I suggest creating a totally new calendar to import into, in case something breaks):
                <br>
                <img src="static/cal_tut_3.png">
                <br>
                <img src="static/cal_tut_4.png">
            </body>
        </html>
    """

@app.route('/fixSchedule', methods=["POST"])
def transform_view():
    file = request.files['data_file']
    year = request.args.get('year')
    hadassah_start_times = 'hadassah_start_times' in request.form
    if not file:
        return "No file"

    file_contents = file.stream.readlines()

    result = fixer.fix(file_contents, year, hadassah_start_times)

    generator = (line + '\n' for line in result)

    return Response(generator, mimetype="text/plain", headers={"Content-Disposition":"attachment;filename=fixed_schedule.ics"})