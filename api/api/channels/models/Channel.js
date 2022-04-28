const { Schema, model } = require('mongoose');
const mongoosePaginate = require('mongoose-paginate-v2');

const ChannelSchema = new Schema(
    {
        code: {
            type: String,
            required: true,
            unique: true,
        },
        name: String,
        mandatory_fields: [String],
    },
    {
        timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' },
    },
);

ChannelSchema.plugin(mongoosePaginate);
module.exports = model('gip_channels', ChannelSchema);
