const path = require('path');
const CopyWebpackPlugin = require('copy-webpack-plugin');


module.exports = {
    mode: 'none',
    entry: '.' + path.sep + path.join('src_js', 'opcut', 'main'),
    output: {
        filename: 'main.js',
        path: path.join(__dirname, 'build', 'js')
    },
    module: {
        rules: [
            {
                test: /\.scss$/,
                use: ["style-loader", "css-loader", "resolve-url-loader", "sass-loader?sourceMap"]
            },
            {
                test: /\.woff2$/,
                use: "file-loader?name=fonts/[name].[ext]"
            }
        ]
    },
    resolve: {
        modules: [
            path.join(__dirname, 'src_js'),
            path.join(__dirname, 'src_scss'),
            path.join(__dirname, 'node_modules')
        ]
    },
    watchOptions: {
        ignored: /node_modules/
    },
    plugins: [
        new CopyWebpackPlugin([{from: 'src_web'}])
    ],
    devtool: 'source-map',
    stats: 'errors-only'
};
