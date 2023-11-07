#　横スクロールシューティング

## 実行環境の必要条件
* python >= 3.10
* pygame >= 2.1

## ゲーム概要
主人公をキーボード操作で何かを発射し敵を倒すゲーム
* クリア条件: ボスの撃破

## ゲーム実装
### 共通基本機能
* 背景画像と主人公キャラクターの描画　msou_kokatonがベースになっている

### 担当追加機能
* ボスについての機能（担当：市川）：条件を満たすと通常の敵より強く設定された敵（ボス）が登場する機能 弾を２０回ヒットさせると倒す  通常の敵より大きめの爆弾を高頻度で自機に向かって飛ばす
* 背景画像と主人公キャラクターの描画
* 背景画像：宇宙
* 主人公キャラクター:飛行機
* 自機に関する設定(担当:伊藤)：飛行機を描画し飛行機の残機のクラス作成やボムが当たった時の数秒間無敵状態になるように作成、飛行機の残機が０になった時、ゲームーオーバーを表示表示させるクラス作成
* 背景画像と主人公キャラクターの描画
* 基礎プログラムはsumou_kokaton.py（配布）
* スコアに応じたビームの変化に関する機能（担当:安西）：スコアに応じて自キャラクターが発射するビームを変化させる機能
* それぞれスコア50で弾速の向上
* スコア100で弾の大きさを変更
* スコア200で発射される弾が増加
* アイテムについての機能（担当：栁下）：200フレーム（雑魚敵と同じ）ごとに回復薬が生成される。10%の確率で毒薬が生成される。
　回復薬と接触すると黄色いエフェクトがその場に発生する。毒薬であった場合、緑色のエフェクトが発生する。
　他チームメンバーが作成する「残機機能」と連動して、残機量に変化をもたらす予定。接触したアイテムが回復薬か毒薬かの判定はプログラム済み。