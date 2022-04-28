/* eslint-disable-next-line */
const path = require('path');
// const createError = require('http-errors');
const express = require('express');
const cookieParser = require('cookie-parser');
const logger = require('morgan');
const bodyParser = require('body-parser');

// mongodb
/* eslint-disable-next-line */
const db = require('./helpers/db')();

const app = express();

app.use(bodyParser.json());
app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());

app.use((req, res, next) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'OPTIONS, GET, POST, PUT, PATCH, DELETE');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    next();
});

// IMPORT ROUTES
const attributesRouter = require('./attributes/routes');
const authRouter = require('./auth/routes');
const categoriesRouter = require('./categories/routes');
const channelRouter = require('./channels/routes');
const itemRouter = require('./items/routes');
const listRouter = require('./lists/routes');

// DEFINE ROUTES
app.use('/attributes/', attributesRouter);
app.use('/auth/', authRouter);
app.use('/categories/', categoriesRouter);
app.use('/channels/', channelRouter);
app.use('/items/', itemRouter);
app.use('/lists/', listRouter);


app.use(logErrors);
app.use(errorHandler);
app.use(clientErrorHandler);

function logErrors(err, req, res, next) {
    console.error(err.stack);
    next(err);
}

function errorHandler(err, req, res, next) {
    res.status(500);
    res.render('error', { error: err });
}

function clientErrorHandler(err, req, res, next) {
    if (req.xhr) {
        res.status(500).send({ error: 'Something failed!' });
    } else {
        next(err);
    }
}
module.exports = app;
