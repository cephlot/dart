const express = require('express')
const app = express()
const port = 3000
var bodyParser = require('body-parser');


let fs = require('fs');
let obj = {"1": "0", "2": "0"}

app.set('view engine', 'pug')
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ 
	extended: true 
 }));

app.get('/', (_req, res) => {
    res.render('index', { 
		p1_score: obj['1'],
		p2_score: obj['2']
	 })
})

app.put('/', (req, res) => {
    obj = req.body

	  res.render('index', { 
		p1_score: obj['1'],
		p2_score: obj['2']
	 })
})

app.post('/', (req, res) => {
    obj = req.body

	console.log(req.body)

	res.render('index', { 
		p1_score: obj['1'],
		p2_score: obj['2']
	 })})

app.delete('/', (_req, res) => {
	obj = {1: 0, 2: 0};

	res.render('index', { 
		p1_score: obj['1'],
		p2_score: obj['2']
	 })})

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`)
})