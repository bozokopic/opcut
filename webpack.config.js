var path = require('path');
var fs = require('fs');
var webpack = require('webpack');

// moment locales hack
var momentLocalePath = path.join(
    __dirname, 'node_modules', 'moment', 'src', 'lib', 'locale', 'locale');
if (!fs.existsSync(momentLocalePath)) {
    fs.mkdirSync(momentLocalePath);
}

module.exports = {
    entry: {
        main: '.' + path.sep + path.join('src_js', 'opcut', 'main')
    },
    output: {
        filename: '[name].js',
        path: path.join(__dirname, 'build', 'jsopcut'),
        pathinfo: true
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: [/node_modules(?!(\/moment\/src)|(\\moment\\src))/],
                loader: 'babel-loader',
                options: {
                    presets: [['es2015', {modules: false}]],
                    plugins: []
                    // plugins: ["transform-runtime",
                    //           "transform-decorators",
                    //           ["transform-async-to-module-method",
                    //            {module: "bluebird",
                    //             method: "coroutine"}]],
                    // retainLines: true
                }
            },
            {
                test: /\.scss$/,
                use: ["style-loader", "css-loader", "resolve-url-loader", "sass-loader?sourceMap"]
            },
            {
                test: /(\/|\\)buffer(\/|\\)index\.js$/,
                use: 'imports-loader?global=>window'
            },



            { test: /\.woff(\?v=\d+\.\d+\.\d+)?$/, use: "url-loader?name=fonts/[hash].[ext]&limit=10000&mimetype=application/font-woff" },
            { test: /\.woff2(\?v=\d+\.\d+\.\d+)?$/, use: "url-loader?name=fonts/[hash].[ext]&limit=10000&mimetype=application/font-woff" },
            { test: /\.ttf(\?v=\d+\.\d+\.\d+)?$/, use: "url-loader?name=fonts/[hash].[ext]&limit=10000&mimetype=application/octet-stream" },
            { test: /\.eot(\?v=\d+\.\d+\.\d+)?$/, use: "file-loader?name=fonts/[hash].[ext]" },
            { test: /\.svg(\?v=\d+\.\d+\.\d+)?$/, use: "url-loader?name=fonts/[hash].[ext]&limit=10000&mimetype=image/svg+xml" }

        ]
    },
    resolve: {
        modules: [
            path.join(__dirname, 'src_js'),
            path.join(__dirname, 'src_web'),
            path.join(__dirname, 'node_modules')],
        alias: {
            'ByteBuffer': 'bytebuffer',
            'Long': 'long',
            'underscore': 'underscore/underscore',
            'moment': 'moment/src/moment'
        }
    },
    resolveLoader: {
        alias: {
            static: 'file-loader?context=src_web/static&name=[path][name].[ext]',
            template: 'raw'
        }
    },
    externals: [{
        'fs': 'commonjs fs',
        'app': 'commonjs app',
        'browser-window': 'commonjs browser-window',
        'electron': 'commonjs electron',
        'child_process': 'commonjs child_process'
    }],
    node: {
        console: false,
        global: false,
        process: false,
        Buffer: false,
        __filename: false,
        __dirname: false,
        setImmediate: false
    },
    //devtool: 'inline-source-map',
    devtool: 'source-map',
    plugins: [
        //new webpack.optimize.UglifyJsPlugin({compress: {warnings: false}})
    ]
};
