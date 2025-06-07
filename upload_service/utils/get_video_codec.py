import subprocess
import json

def get_video_codec(file_path: str) -> str:
    try:
        # run ffprobe to extract stream info in JSON
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",                          # -v error: suppress logs except errors
                "-select_streams", "v:0",               # -select_streams v:0: choose the first video stream
                "-show_entries", "stream=codec_name",   # -show_entries stream=codec_name: output codec_name field only
                "-of", "json",                          # -of json: output format JSON
                file_path,
            ],
            stdout=subprocess.PIPE, # capture stdout and stderr
            stderr=subprocess.PIPE,
            text=True,              # return output as string 
            check=True              # raise CalledProcessError if command fails
        )

        # parse JSON output from ffprobe
        info = json.loads(result.stdout)

        # extract codec_name from first stream
        return info["streams"][0]["codec_name"]
    except Exception as e:
        print("Error getting codec: ", e)
        return "unknown"