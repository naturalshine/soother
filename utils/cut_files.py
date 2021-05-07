import os
from pathlib import Path

# Import the AudioSegment class for processing audio and the 
# split_on_silence function for separating out silent chunks.
from pydub import AudioSegment
from pydub.silence import split_on_silence
from pydub.playback import play


def debug_length(song, loudness):

    #play(song)


    # Split track where the silence is 2 seconds or more and get chunks using 
    # the imported function.
    chunks = split_on_silence (
        # Use the loaded audio.
        song, 
        # Specify that a silent chunk must be at least 2 seconds or 2000 ms long.
        min_silence_len = 2000,

        # here we set a higher threshhold to try to split apart the longer chunks that
        # probably contain multiple lines
        silence_thresh = -70.0,

        # keep some ms of silence, unfortunately cannot designate end vs beignning
        keep_silence = 500
    )

    return chunks


def cut_file(path, songFile):
    path = path.split("/")
    cut_path_arr = ["cut_files" if x=="files_post" else x for x in path]
    cut_path = "/".join(cut_path_arr) + "/" + songFile[:-4]

    print(cut_path)

    Path(cut_path).mkdir(parents=True, exist_ok=True)

    # if we've already output the files for this dir, skip
    for root, dirs, files in os.walk(cut_path):
        if files: 
            return

    # Load  audio.
    song_path = "/".join(path) + "/" + songFile

    song = AudioSegment.from_wav(song_path)
    loudness = song.dBFS
    print(loudness)


    # Split track where the silence is 2 seconds or more and get chunks using 
    # the imported function.
    chunks = split_on_silence (
        # Use the loaded audio.
        song, 
        # Specify that a silent chunk must be at least 2 seconds or 2000 ms long.
        min_silence_len = 2000,

        # we set a very low silence threshhold cause we're... whispering
        silence_thresh = -74.0,
        
        # keep some ms of silence, unfortunately cannot designate end vs beignning
        keep_silence = 500
    )

    print("PRE POSTPROCESS")
    print(len(chunks))

    chunksToInsert = []
    postProcessChunks = []

    for i, chunk in enumerate(chunks):
        if (len(chunk) > 20000):
            newChunks = debug_length(chunk, loudness)
            postProcessChunks = postProcessChunks + newChunks
 
        else:
            postProcessChunks.append(chunk)

    print("POST PROCESS LENGTH")
    print(len(postProcessChunks))

    # here's the trick - we reverse because in cases of repeated lines, we always want the last take.
    postProcessChunks.reverse()
    finalChunks = []

    for i, d in enumerate(postProcessChunks):
        if len(d) > 1500:
            print("chunk number: {0}/".format(i) + str(len(postProcessChunks)))

            while True:
                try:
                    play(d)
                except KeyboardInterrupt:
                    break

            value = input("Keep chunk? y/n")

            print(f"You entered {value}")

            if not value == "n":
                finalChunks.append(d)

    # we reverse again so tracks are in forward order
    finalChunks.reverse()
    for i, e in enumerate(finalChunks):
        # Create a silence chunk that's 0.5 seconds (or 500 ms) long for padding.
        silence_chunk = AudioSegment.silent(duration=500)

        # Add the padding chunk to beginning and end of the entire chunk.
        audio_chunk = silence_chunk + e + silence_chunk
        audio_chunk = audio_chunk + 10

        # Export the audio chunk with bitrate.
        chunk_path = cut_path + "/{0}.wav"
        print("Exporting {0}.wav.".format(i))
        audio_chunk.export(
            chunk_path.format(i),
            bitrate = 44100,
            format = "wav"
        )





pathVal = input("ENTER FOLDER PATH!")

print(f"You entered {pathVal}")

for root, dirs, files in os.walk(pathVal):
    if files:
        for file in files: 
            if file.endswith(".wav"):
                cut_file(pathVal, file)
    else:
        print("NO FILES!")



