const { Schema, model } = require('mongoose');
const mongoosePaginate = require('mongoose-paginate-v2');

const ListSchema = new Schema(
    {
        /*
        code: {
            type: String,
            required: true,
            unique: true,
        },
        */
        name: String,
        description: String,
        start_date: Date,
        end_date: Date,
        channel: {
            type: Schema.Types.ObjectID,
            ref: 'gip_channels',
        },
        minimum_score: {
            type: Number,
            default: 0,
        },
        items: [
            {
                type: Schema.Types.ObjectID,
                ref: 'gip_items',
            },
        ],
        is_archived: Boolean,
        is_private: Boolean,
        created_by: {
            type: Schema.Types.ObjectID,
            ref: 'gip_users',
        },
        shared_with: [
            {
                type: Schema.Types.ObjectID,
                ref: 'gip_users',
            },
        ],
    },
    {
        timestamps: { createdAt: 'created_at', updatedAt: 'updated_at' },
    },
);

ListSchema.plugin(mongoosePaginate);
module.exports = model('gip_lists', ListSchema);
