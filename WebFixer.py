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
                First, get your schedule file from the rishum-net. This is an *.ics file. You can find it when rishum is active, as described in the following images:
                <br>
                <img src="static/cal_tut_1.png">
                <br>
                <img src="static/cal_tut_2.png">
                <br>
                <form action="/fixSchedule" method="post" enctype="multipart/form-data">
                    Now, upload the *.ics file here: <input type="file" name="data_file" />
                    <br>
                    Enter the school year (E.g., for 2018-19, write 2019) <input type="string" name="year" />
                    <input type="submit" value="Fix"/>
                </form>
            </body>
        </html>
    """

@app.route('/fixSchedule', methods=["POST"])
def transform_view():
    file = request.files['data_file']
    year = request.args.get('year')
    if not file:
        return "No file"

    file_contents = file.stream.readlines()

    result = fixer.fix(file_contents,year)

    generator = (line + '\n' for line in result)

    return Response(generator, mimetype="text/plain", headers={"Content-Disposition":"attachment;filename=fixed_schedule.ics"})