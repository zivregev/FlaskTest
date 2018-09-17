from ScheduleFixer  import app
from flask import make_response, request, Response
from werkzeug.utils import secure_filename
import ScheduleFixer.Fixer as fixer

ALLOWED_EXTENSIONS = set(['ics'])

@app.route('/')
def form():
    return """
        <html>
            <body>
                <h1>Correct HUJI medicine schedule</h1>

                <form action="/fixSchedule" method="post" enctype="multipart/form-data">
                    <input type="file" name="data_file" />
                    <input type="string" name="year" />
                    <input type="submit" />
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