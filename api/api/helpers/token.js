const Token = {
    _keyStr: '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
    randomString(length, chars) {
        let result = '';
        for (let i = length; i > 0; --i) result += chars[Math.floor(Math.random() * chars.length)];
        return result;
    },
    generate(length = 32) {
        return Token.randomString(length, Token._keyStr);
    },
};

module.exports = Token;
