# Animal Speech Understanding &amp; Unsupervised Translation

#### Xeno-Canto dataset access

To download audio samples from Xeno-Canto dataset run

```bash
python xeno-canto_request.py --max_pages 10 \
    --filename "xeno-canto/recordings.csv" \
    --output_dir "xeno-canto/audio_files" \
    --query "cnt:brazil"
```
Instructions for creating specific queries available [here](https://xeno-canto.org/explore/api).
