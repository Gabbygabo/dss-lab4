1. Before, we just used a Jupyter Notebook with hardcoded paths in our own laptops. Since there's no Docker, it easily breaks if someone else tries it on their computer because they have different package version.

2. The original file is the real truth. The raw copy just keep it safe from our database. Curated is the cleaned version, and model-ready is the one we did encoding on so the Random Forest can use it.

3. I used the run_id and primary keys in the postgres table to stop duplicates. This works assuming the source data have its own unique ID for each sensor.

4. I just injected a fake run_id (like what I did with local_20261013) using the CLI. It just tracks the pipeline run instead of pretending its a real time stamp from the factory.

5. Staging is just for basic fixing like data types so it fits in the database. Curated is for the heavy lifting like dropping nulls and one-hot encoding, because that actually changes the data for the ML model.

6. Parquet is really fast for our model to read. But you shouldn't use it for everything, especially if your database needs to write a lot of data constantly.

7. If the pipeline isn't idempotent, Airflow will just insert the same data again. This duplicates everything and ruins the model training because the data is skewed.

8. Because I set primary keys in Postgres. If Airflow retries, the database will just block the duplicate rows so the row count stays exactly the same.

9. Checking if columns are missing is the most important one. If a feature column is missing, the model will just fail silently and give bad predictions.

10. I used the exact same 80/20 chronological split and set the random_state to 42. This makes sure it picks the exact same rows every time it runs.

11. Even with Docker, different laptop hardware can calculate decimals slightly different. This can change the final numbers a tiny bit depending on the OS.

12. You have to check it step by step. First check if the raw file checksum match, then check the row counts in the database, and finally the train/test splits to see where it actually went wrong.

13. I'd watch out for pipeline crashes and how long it takes to run. I would also monitor the metrics to see if the RMSE gets worse than our 3.24 baseline.

14. Doing the Pandas transformations locally in Airflow would bottleneck first. Like what happened to my laptop with the memory crashes, we would need to move the processing to the cloud or use PySpark instead.

15. I would put strict access controls so not everyone can run the DAGs or look at the database. Also I'd mask or encrypt the sensitive parts in the staging area so people can't read it.