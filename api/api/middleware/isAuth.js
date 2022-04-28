const jwt = require('jsonwebtoken');
const Token = require('../auth/models/tokens');
const User = require('../users/models/users');
const currentUser = require('../auth/controllers');

module.exports = async (req, res, next) => {
    const authHeader = req.get('Authorization');
    if (!authHeader) {
        const error = new Error('Not authenticated.');
        error.statusCode = 401;
        throw error;
    }
    const token = authHeader.split(' ')[1];
    const dbToken = await Token.findOne({ token });
    if (dbToken) {
        const username = dbToken.username;
        User.findOne({ office_ref: username }).then(user => {
            req.userId = user._id;
            currentUser.setcurrentUser(req.userId);
            next();
        });
    } else {
        let decodedToken;
        try {
            decodedToken = jwt.verify(token, process.env.SECRET_KEY);
        } catch (err) {
            err.statusCode = 500;
            throw err;
        }
        if (!decodedToken) {
            const error = new Error('Not authenticated.');
            error.statusCode = 401;
            throw error;
        }
        req.userId = decodedToken.userId;
        await currentUser.setcurrentUser(req.userId);
        next();
    }
};
