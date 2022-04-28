const { Schema, model } = require('mongoose');

const TokenSchema = new Schema(
    {
        username: String,
        token: String,
    },
    {
        timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' },
    },
);

module.exports = model('gip_tokens', TokenSchema);
