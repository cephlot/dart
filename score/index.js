const express = require('express')
const app = express()
const port = 3000
const path = require('path');

let fs = require('fs');
let obj = [{1: 'one'}, {2: 'two'}, {3: 'three'}]

app.set('view engine', 'pug')


app.get('/', (req, res) => {
    res.render('index', { 
		p1_score: 323,
		p2_score: 131
	 })
})

app.put('/', (req, res) => {
    obj.push(req)

    let result = '<table>';
    for (let el in obj) {
        result += "<tr><td>" + el + "</td><td>" + el[0] + "</td></tr>";
      }
      result += '</table>';

    res.send(result)
})

app.post('/', (req, res) => {
    obj.push(req)

    res.send(document.getElementById(req.id).getElementsByTagName('div')[0] = 'hej');
})

app.delete('/', (req, res) => {
    res.send('Got: DELETE')
})

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`)
})