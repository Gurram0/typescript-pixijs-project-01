const path = require('path');
const webpack = require('webpack');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const CopyPlugin = require('copy-webpack-plugin');

module.exports = env => {
    const platform = env.platform || 'desktop';
    const isProduction = env.mode === 'production';
    const isMobile = platform === 'mobile';
    const bundleSuffix = isProduction ? '.min' : '';

    const plugins = [
        new webpack.ProvidePlugin({
            PIXI: 'pixi.js',
        }),
        new webpack.DefinePlugin({
            __DEV__: !isProduction,
            __PROD__: isProduction,
            __MOBILE__: isMobile,
            __DESKTOP__: !isMobile,
            __PLATFORM__: `${platform}`,
        }),
        new webpack.DefinePlugin({
            'process.platform': env.platform,
        }),
        new HtmlWebpackPlugin({
            template: path.join(__dirname, 'sources/index.html'),
            minify: false,
        }),
        new CopyPlugin({
            patterns: [
                {
                    from: 'node_modules/core-pixi-webpack/lib/assets',
                    to: 'assets',
                    force: false,
                    noErrorOnMissing: true
                },
                {
                    from: 'assets',
                    to: 'assets',
                    force: true,
                    noErrorOnMissing: true,
                },
                {
                    from: 'data',
                    to: 'data',
                    force: true,
                    noErrorOnMissing: true,
                }
            ],
        }),
        new webpack.HotModuleReplacementPlugin(),
    ];

    return {
        devtool: isProduction ? false : 'source-map',
        mode: env.mode,
        entry: {
            main: './sources/main.ts',
        },
        output: {
            path: path.resolve(__dirname, isProduction ? './prod_bin' : './dev_bin'),
            filename: `${platform}.bundle${bundleSuffix}.js`
        },
        optimization: {
            sideEffects: false,
            usedExports: true,
            minimize: isProduction,
            minimizer: [
                compiler => {
                    const TerserPlugin = require('terser-webpack-plugin');
                    new TerserPlugin({
                        terserOptions: {
                            ecma: undefined,
                            parse: {},
                            compress: {toplevel:true,passes:2,hoist_funs:true,hoist_props:true},
                            mangle: {toplevel:true,keep_classnames:true,keep_fnames:false,module:false},
                            module: true
                        },
                    }).apply(compiler);
                },
            ],
        },
        module: {
            rules: [
                {
                    test: /\.ts?$/,
                    loader: 'ts-loader',
                    exclude: /node_modules/
                },
                { 
                    test: /\.js$/,
                    enforce: "pre",
                    loader: 'source-map-loader'
                },
                {
                    test: /\.(?:ico|gif|png|jpg|jpeg|webp|atlas)$/i,
                    issuer: /\.css$/,
                    type: 'asset/resource',
                    use: [
                        {
                            loader: 'file-loader',
                            options: {
                                name: '[name].[ext]',
                            },
                        },
                    ],
                },
                {
                    test: /\.(woff(2)?|eot|ttf|otf|svg|)$/,
                    type: 'asset/inline',
                    use: [
                        {
                            loader: 'file-loader',
                            options: {
                                name: '[name].[ext]',
                            },
                        },
                    ],
                },
            ],
        },
        resolve: {
            extensions: ['.tsx', '.ts', '.js'],
            fallback: {
                path: require.resolve('path-browserify')
            },
        },
        devServer: {
            static: isProduction ? './prod_bin' : './dev_bin',
            client: {
                overlay: false,
                progress: true
            },
            open: {
                target: ['#{"sid":"Se24463652b66"}'],
                app: {
                    name: 'chrome',
                    arguments: ['--incognito', '--new-window'],
                }
            },
            allowedHosts: ['localhost', '.localhost'],
            historyApiFallback: true,
            liveReload: true,
            compress: true,
            hot: true,
            host: '0.0.0.0',
            port: 8081
        },
        plugins
    };
};
