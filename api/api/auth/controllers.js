const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const User = require('../users/models/users');
const Token = require('./models/tokens');
const TokenHelper = require('../helpers/token');

function finishLogin(user, response) {
    const jwtSign = { username: user.office_ref, userId: user._id };
    const token = jwt.sign(jwtSign, process.env.SECRET_KEY, {
        expiresIn: '8h', // it will expire token after 8h hours and if the user then refresh the page will log out
    });
    response.status(200).json({ token });
}

exports.postCreateUser = async (request, response, next) => {
    const { username, password } = request.body;
    try {
        const existUser = await User.findOne({ office_ref: username });
        if (existUser) {
            const error = new Error('User already exist');
            response.status(409).json({
                error: 'User already exist',
            });
            error.statusCode = 409;
            throw error;
        }
        const hashPassword = await bcrypt.hash(password, 8);
        const user = new User({
            office_ref: username,
            password: hashPassword,
        });
        const result = await user.save();
        response.status(200).json(result);
    } catch (err) {
        if (!err.statusCode) {
            err.statusCode = 500;
        }
        next(err);
    }
};

let loadedUser = {
    _id: null,
    office_ref: null,
    access_level: null,
};
exports.postLoginUser = async (request, response, next) => {
    const { username, password } = request.body;

    try {
        const user = await User.findOne({ office_ref: username });
        const error = new Error('User not found or password is not match');
        if (!user) {
            error.statusCode = 401;
            throw error;
        }
        const comparePassword = bcrypt.compare(password, user.password);
        if (!comparePassword) {
            error.statusCode = 401;
            throw error;
        }
        loadedUser = user;
        finishLogin(user, response);
    } catch (err) {
        if (!err.statusCode) {
            err.statusCode = 500;
        }
        next(err);
    }
};

exports.postIntranetLogin = async (request, response, next) => {
    const { username } = request.body;
    let user = await User.findOne({ office_ref: username });
    if (!user) {
        const newPass = `${username}_${TokenHelper.generate()}`;
        const hashPassword = await bcrypt.hash(newPass, 8);
        user = new User({
            office_ref: username,
            password: hashPassword,
        });
        await user.save();
    }
    loadedUser = user;
    finishLogin(user, response);
};

exports.getUser = (request, response) => {
    if (loadedUser) {
        response.status(200).json(exports.currentUser());
    } else {
        response.status(500).json({ error: 'No user loggued' });
    }
};

exports.postCreateToken = (request, response) => {
    new Token(request.body)
        .save()
        .then(data => {
            response.status(200).json(data);
        })
        .catch(err => {
            response.status(404).json(err);
        });
};

exports.getToken = (request, response) => {
    Token.find({})
        .then(data => {
            response.status(200).json(data);
        })
        .catch(err => {
            response.status(404).json(err);
        });
};

exports.currentUser = () => {
    return {
        user: {
            id: loadedUser._id,
            office_ref: loadedUser.office_ref,
            access_level: loadedUser.access_level,
        },
    };
};

exports.setcurrentUser = async objectId => {
    if (objectId == null) {
        return null;
    }
    if (loadedUser.id == null || objectId !== loadedUser.id) {
        loadedUser = await User.findById(objectId);
    }
    return exports.currentUser();
};
