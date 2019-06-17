# coding=utf-8
import logging
import time

log = logging.getLogger('logica')


class LogicaPI:

    def __init__(self):
        self.inicio_ciclo_abb = False
        self.triac_posicao_ok = False

        self.saida_flex = 0
        self.verificacao_ok = False

        self.digital_abb = 0b00

        # todo - atualizar DO

        self.triac_ir_home()
        self.triac_ir_posicao()

    def triac_ir_home(self):
        # Todo - MDI
        pass

    def triac_ir_posicao(self):
        # Todo - mdi
        pass

    # Comando do operador
    def celula_iniciar_ciclo_individual(self):
        self.inicio_ciclo_abb = True
        # todo - atualizar DO
        time.sleep(0.1)
        self.inicio_ciclo_abb = False
        # todo - atualizar DO

    # Comando do operador
    def celula_iniciar_ciclo_continuo(self):
        self.inicio_ciclo_abb = True
        # todo - atualizar DO

    # Comando do operador
    def celula_parar_ciclo_continuo(self):
        self.inicio_ciclo_abb = False
        # todo - atualizar DO

    # Rodado continuamente pra determinar ação em caso de comando da ABB
    def verificar_comando_abb(self):
        # todo - atualizar DI

        # Aguardamos 100ms caso as entradas não sejam 00, pra ter certeza de que as entradas tiveram tempo de
        # ser setadas corretamente
        if self.digital_abb != 0b00:
            time.sleep(0.1)
            # todo - atualizar DI

        if self.digital_abb == 0b01:
            self.verificar_peca_boa()
        elif self.digital_abb == 0b10:
            self.triac_iniciar_operacao()
        elif self.digital_abb == 0b11:
            self.verificar_tem_peca_triac()

    # Comando do ABB
    def triac_iniciar_operacao(self):
        self.triac_posicao_ok = False
        # todo - atualizar DO
        # todo - MDI triac operação
        # todo - verificar fluxograma (triac posição OK?)

    # Comando do ABB
    def verificar_tem_peca_triac(self):
        # todo - alg. visão
        tem_peca = input('Tem peça triac? (s/n)')
        tem_peca = tem_peca.strip().lower() in ['s', 'y', '1']
        if tem_peca:
            self.saida_flex = 1
            # todo - atualizar DO
            self.verificacao_ok = True
            # todo - atualizar DO
        else:
            self.saida_flex = 0
            # todo - atualizar DO
            self.verificacao_ok = True
            # todo - atualizar DO
        time.sleep(0.1)
        self.verificacao_ok = False
        # todo - atualizar DO

    # Comando do ABB
    def verificar_peca_boa(self):
        # todo - alg. visão
        peca_boa = input('Peça boa? (s/n)')
        peca_boa = peca_boa.strip().lower() in ['s', 'y', '1']
        if peca_boa:
            self.saida_flex = 1
            # todo - atualizar DO
            self.verificacao_ok = True
            # todo - atualizar DO
        else:
            self.saida_flex = 0
            # todo - atualizar DO
            self.verificacao_ok = True
            # todo - atualizar DO
        time.sleep(0.1)
        self.verificacao_ok = False
        # todo - atualizar DO


lpi = LogicaPI()
lpi.celula_parar_ciclo_continuo()
