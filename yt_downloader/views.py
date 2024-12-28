from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, FileResponse
from pytubefix import YouTube
import re
import os
import ffmpeg

# Define video folder for temporary storage
video_folder = '/tmp/videos'
if not os.path.exists(video_folder):
    os.makedirs(video_folder)

# Utility function to sanitize filenames
def sanitize_filename(filename):
    print(f"Sanitizing filename: {filename}")
    return re.sub(r'[\\/*?:"<>|]', "_", filename)

# Index view
def index(request):
    print("Rendering index page.")
    return render(request, 'yt_downloader/download_video.html')

# Handle video download and resolution selection
def download_video(request):
    print("download_video view called.")
    if request.method == 'POST':
        video_url = request.POST.get('url', '')
        print(f"Video URL received: {video_url}")
        if not video_url:
            print("No video URL provided.")
            return JsonResponse({"error": "Please provide a YouTube URL."}, status=400)
        try:
            yt = YouTube(video_url)
            print(f"Fetched video details: Title={yt.title}, Length={yt.length}s")
            streams = yt.streams.filter(adaptive=True, file_extension="mp4", only_video=True).order_by('resolution').desc()
            available_resolutions = [
                {
                    "resolution": stream.resolution,
                    "fps": stream.fps,
                    "size": f"{stream.filesize // (1024 * 1024)} MB" if stream.filesize else "unknown"
                }
                for stream in streams
            ]
            print(f"Available resolutions: {available_resolutions}")
            return render(request, 'yt_downloader/select_resolution.html', {
                'video_url': video_url,
                'available_resolutions': available_resolutions
            })
        except Exception as e:
            print(f"Error fetching video info: {str(e)}")
            return JsonResponse({"error": f"Error fetching video info: {str(e)}"}, status=500)
    print("Rendering download video page.")
    return render(request, 'yt_downloader/download_video.html')

# Handle resolution-based video download
def start_download(request):
    print("start_download view called.")
    if request.method == 'POST':
        video_url = request.POST.get('url')
        resolution = request.POST.get('resolution')
        print(f"Video URL: {video_url}, Resolution: {resolution}")
        if not resolution:
            print("No resolution selected.")
            return JsonResponse({"error": "No resolution selected."}, status=400)
        try:
            yt = YouTube(video_url)
            stream = yt.streams.filter(res=resolution, file_extension="mp4").first()
            if not stream:
                print(f"Resolution {resolution} not available.")
                return JsonResponse({"error": f"Resolution {resolution} not available."}, status=400)
            output_file = sanitize_filename(f"{yt.title}-{resolution}.mp4")
            print(f"Downloading video: {output_file}")
            result = download_video_file(stream, output_file, video_url)
            if result == "Completed":
                print(f"Download completed, redirecting to: download_file/{output_file}")
                return redirect('download_file', filename=output_file)
            else:
                print("Download or merging failed.")
                return JsonResponse({"error": "Error during download or merging."}, status=500)
        except Exception as e:
            print(f"Error downloading video: {str(e)}")
            return JsonResponse({"error": f"Error downloading video: {str(e)}"}, status=500)
    return JsonResponse({"error": "Invalid request method."}, status=405)


# Utility to download and merge video and audio
#---------------------
# def download_video_file(stream, output_file, video_url):
#     try:
#         yt = YouTube(video_url)
#         audio_stream = yt.streams.filter(only_audio=True, file_extension="mp4").first()

#         if not audio_stream:
#             print("No audio streams available for this video.")
#             return

#         print("\nDownloading video...")
#         video_file = stream.download(output_path=video_folder, filename="video.mp4")
#         print("Video downloaded!")

#         print("\nDownloading audio...")
#         audio_file = audio_stream.download(output_path=video_folder, filename="audio.mp4")
#         print("Audio downloaded!")

#         # Merge video and audio using ffmpeg-python
#         output_path = os.path.join(video_folder, output_file)
#         print("\nMerging video and audio...")
#         video_input = ffmpeg.input(os.path.join(video_folder, "video.mp4"))
#         audio_input = ffmpeg.input(os.path.join(video_folder, "audio.mp4"))
#         ffmpeg.output(video_input, audio_input, output_path, vcodec='copy', acodec='aac').run(overwrite_output=True)

#         print(f"Download and merge complete! File saved as '{output_file}'")
#         os.remove(os.path.join(video_folder, "video.mp4"))
#         os.remove(os.path.join(video_folder, "audio.mp4"))
#         return "Completed"
#     except Exception as e:
#         print(f"Error downloading or merging video: {str(e)}")
#---------------------
def download_video_file(stream, output_file, video_url):
    try:
        # print(f"Starting download for video: {video_url}")
        yt = YouTube(video_url)
        audio_stream = yt.streams.filter(only_audio=True, file_extension="mp4").first()
        if not audio_stream:
            # print("No audio streams available for this video.")
            return

        # print("\nDownloading video...")
        video_file = stream.download(output_path=video_folder, filename="video.mp4")
        # print("Video downloaded!")

        # print("\nDownloading audio...")
        audio_file = audio_stream.download(output_path=video_folder, filename="audio.mp4")
        # print("Audio downloaded!")

        # Merge video and audio using ffmpeg-python
        output_path = os.path.join(video_folder, output_file)
        print("\nMergi/ng video and audio...")
        video_input = ffmpeg.input(os.path.join(video_folder, "video.mp4"))
        audio_input = ffmpeg.input(os.path.join(video_folder, "audio.mp4"))
        ffmpeg.output(video_input, audio_input, output_path, vcodec='copy', acodec='aac').run(overwrite_output=True)

        # print(f"Download and merge complete! File saved as '{output_file}'")
        os.remove(os.path.join(video_folder, "video.mp4"))
        os.remove(os.path.join(video_folder, "audio.mp4"))
        return "Completed"
    except Exception as e:
        # print(f"Error downloading or merging video: {str(e)}")
        return
    
# Serve downloaded files
# -----------------
# def download_file(filename):
#     try:
#         return send_from_directory(video_folder, filename, as_attachment=True)
#     except FileNotFoundError:
#         return jsonify({"error": "File not found"}), 404
# -----------------

def download_file(request, filename):
    file_path = os.path.join(video_folder, filename)
    print(f"Serving file: {file_path}")
    try:
        return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return JsonResponse({"error": "File not found"}, status=404)
