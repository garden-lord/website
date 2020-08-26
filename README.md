Before you run this, you should install Conda

```bash
curl -L https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -o conda.sh
bash conda.sh
conda activate
```

To get the code, run

```bash
git clone https://github.com/garden-lord/website.git
cd website
pip install -r requirements.txt
echo '{}' > database.json
```

You need to set up a project so Google log ins will work. To do that, follow step 1 [here](https://github.com/singingwolfboy/flask-dance-google#step-1-get-oauth-credentials-from-google) to get a client ID and a client secret. Then create a file called `google_config.json` in the `website` directory, and put in your info like so:

```json
{
    "client_id": "your client id here",
    "secret": "your secret here"
}
```

Finally, run the server

```bash
python server.py
```

Check that it's working by going to [http://localhost:5000/](http://localhost:5000/) in your browser.