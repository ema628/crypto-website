from dal import autocomplete

from django import forms
import requests, json


CHOICE_LIST = [['aave', 'Aave'], ['akash-network', 'Akash Network'], ['algorand', 'Algorand'], ['aptos', 'Aptos'], ['arbitrum', 'Arbitrum'], ['fetch-ai', 'Artificial Superintelligence Alliance'], ['arweave', 'Arweave'], ['avalanche-2', 'Avalanche'], ['axie-infinity', 'Axie Infinity'], ['beam-2', 'Beam'], ['bitcoin', 'Bitcoin'], ['bitcoin-cash', 'Bitcoin Cash'], ['bitcoin-cash-sv', 'Bitcoin SV'], ['bitget-token', 'Bitget Token'], ['bittensor', 'Bittensor'], ['bittorrent', 'BitTorrent'], ['binancecoin', 'BNB'], ['bonk', 'Bonk'], ['based-brett', 'Brett'], ['cardano', 'Cardano'], ['celestia', 'Celestia'], ['chainlink', 'Chainlink'], ['coredaoorg', 'Core'], ['cosmos', 'Cosmos Hub'], ['crypto-com-chain', 'Cronos'], ['dai', 'Dai'], ['dogecoin', 'Dogecoin'], ['dogwifcoin', 'dogwifhat'], ['dydx-chain', 'dYdX'], ['eos', 'EOS'], ['ethena-usde', 'Ethena USDe'], ['ether-fi-staked-eth', 'ether.fi Staked ETH'], ['ethereum', 'Ethereum'], ['ethereum-classic', 'Ethereum Classic'], ['ethereum-name-service', 'Ethereum Name Service'], ['fantom', 'Fantom'], ['fasttoken', 'Fasttoken'], ['filecoin', 'Filecoin'], ['first-digital-usd', 'First Digital USD'], ['flare-networks', 'Flare'], ['floki', 'FLOKI'], ['flow', 'Flow'], ['gala', 'GALA'], ['gatechain-token', 'Gate'], ['hedera-hashgraph', 'Hedera'], ['immutable-x', 'Immutable'], ['injective-protocol', 'Injective'], ['internet-computer', 'Internet Computer'], ['jasmycoin', 'JasmyCoin'], ['jupiter-exchange-solana', 'Jupiter'], ['kaspa', 'Kaspa'], ['kelp-dao-restaked-eth', 'Kelp DAO Restaked ETH'], ['kucoin-shares', 'KuCoin'], ['leo-token', 'LEO Token'], ['lido-dao', 'Lido DAO'], ['staked-ether', 'Lido Staked Ether'], ['litecoin', 'Litecoin'], ['maker', 'Maker'], ['mantle', 'Mantle'], ['mantle-staked-ether', 'Mantle Staked Ether'], ['mantra-dao', 'MANTRA'], ['msol', 'Marinade Staked SOL'], ['monero', 'Monero'], ['elrond-erd-2', 'MultiversX'], ['near', 'NEAR Protocol'], ['neo', 'NEO'], ['notcoin', 'Notcoin'], ['okb', 'OKB'], ['ondo-finance', 'Ondo'], ['optimism', 'Optimism'], ['pepe', 'Pepe'], ['polkadot', 'Polkadot'], ['matic-network', 'Polygon'], ['pyth-network', 'Pyth Network'], ['quant-network', 'Quant'], ['render-token', 'Render'], ['renzo-restaked-eth', 'Renzo Restaked ETH'], ['rocket-pool-eth', 'Rocket Pool ETH'], ['sei-network', 'Sei'], ['shiba-inu', 'Shiba Inu'], ['solana', 'Solana'], ['blockstack', 'Stacks'], ['starknet', 'Starknet'], ['stellar', 'Stellar'], ['sui', 'Sui'], ['tether', 'Tether'], ['tezos', 'Tezos'], ['the-graph', 'The Graph'], ['theta-token', 'Theta Network'], ['thorchain', 'THORChain'], ['tokenize-xchange', 'Tokenize Xchange'], ['the-open-network', 'Toncoin'], ['tron', 'TRON'], ['uniswap', 'Uniswap'], ['usd-coin', 'USDC'], ['vechain', 'VeChain'], ['whitebit', 'WhiteBIT Coin'], ['wrapped-bitcoin', 'Wrapped Bitcoin'], ['wrapped-eeth', 'Wrapped eETH'], ['ripple', 'XRP']]



currencies = [['usd', "$ USD"],["jpy","¥ JPY"],["gbp","£ GBP"]]
times = [["1", "1 day"], ["7", "1 week"], ["30", "1 month"], ["183", "6 months"], ["365", "1 year"], ["max", "Max"]]

class CoinAutocompleteFromList(autocomplete.Select2ListView):
    def get_list(self):
        return CHOICE_LIST


class CoinForm(forms.Form):
    Coin_1 = autocomplete.Select2ListChoiceField(
        choice_list=CHOICE_LIST,
        widget=autocomplete.ListSelect2(url='coin-autocomplete')
    )
    Coin_2 = autocomplete.Select2ListChoiceField(
        choice_list=CHOICE_LIST,
        widget=autocomplete.ListSelect2(url='coin-autocomplete')
    )
    Currency = forms.ChoiceField(choices=currencies)
    Time_range_for_graph = forms.ChoiceField(choices=times)

class form2(forms.Form):
    Search_for_a_coin = autocomplete.Select2ListChoiceField(
        choice_list=CHOICE_LIST,
        widget=autocomplete.ListSelect2(url='coin-autocomplete')
    )

class form3(forms.Form):
    Compare_with_another_coin = autocomplete.Select2ListChoiceField(
        choice_list=CHOICE_LIST,
        widget=autocomplete.ListSelect2(url='coin-autocomplete')
    )

class bookmark(forms.Form):
    bookmark_this_page=forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={'onchange': 'submit();'}))
