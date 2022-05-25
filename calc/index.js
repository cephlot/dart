// index.js

const express = require('express')
const {spawn} = require('child_process');
const app = express()
const port = 3000

app.get('/', (_, res) => {
    res.json(["Hello, world!"]);
})

app.listen(port, () => console.log('App listening to on port 3000'))