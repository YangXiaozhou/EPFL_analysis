lines_to_be_outed = [1, 4, 7, 10, 14, 18, 21, 24, 30, 34]
samples_per_line = 100
training_data = pd.DataFrame()

start_time = time.time()
for line in lines_to_be_outed:
    for i in range(samples_per_line):
        pmu_0_va_degree = []
        pmu_1_va_degree = []
        pmu_2_va_degree = []

        pmu_0_vm_pu = []
        pmu_1_vm_pu = []
        pmu_2_vm_pu = []

        pmu_data = pd.DataFrame()
        for j in range(len(pmu_location)):
            pmu_data['pmu_'+str(j)+'_va_degree'] = []
            pmu_data['pmu_'+str(j)+'_vm_pu'] = []

        net_39 = pandapower.networks.case39()
        rename(net_39)
        pp.runpp(net_39)

        # For a PMU with 60 sps
        for t in range(samples_per_second):
            change_loads(net_39, loads.loc[t])
            pp.runpp(net_39)
            record_pmu_data(net_39, pmu_index)

        pmu_data = pd.DataFrame(list(zip(pmu_0_va_degree, pmu_0_vm_pu, 
                                    pmu_1_va_degree, pmu_1_vm_pu, pmu_2_va_degree, 
                                    pmu_2_vm_pu)), columns=pmu_data.columns)

        # Setting a line to in service or not
        line_number = line
        net_39.line.in_service.loc[line_number-1] = False
        net_39.line.loc[line_number-1]

        # For a PMU with 60 sps
        for t in range(samples_per_second):
            change_loads(net_39, loads.loc[t])
            pp.runpp(net_39)
            record_pmu_data(net_39, pmu_index)

        pmu_data = pd.DataFrame(list(zip(pmu_0_va_degree, pmu_0_vm_pu, 
                                    pmu_1_va_degree, pmu_1_vm_pu, pmu_2_va_degree, 
                                    pmu_2_vm_pu)), columns=pmu_data.columns)


        fft_pmu0 = np.fft.fft(pmu_data.pmu_0_va_degree)
        fft_pmu1 = np.fft.fft(np.asarray(pmu_data.pmu_1_va_degree)-np.asarray(pmu_data.pmu_0_va_degree))
        fft_pmu2 = np.fft.fft(np.asarray(pmu_data.pmu_2_va_degree)-np.asarray(pmu_data.pmu_0_va_degree))


        imag_pmu0 = fft_pmu0.imag.tolist()
        imag_pmu1 = fft_pmu1.imag.tolist()
        imag_pmu2 = fft_pmu2.imag.tolist()

        predictor = imag_pmu0[60:]
        predictor.append(imag_pmu0[60] - imag_pmu0[59])
        predictor.extend(imag_pmu1[60:])
        predictor.append(imag_pmu1[60] - imag_pmu1[59])
        predictor.extend(imag_pmu2[60:])
        predictor.append(imag_pmu2[60] - imag_pmu2[59])

        training = predictor
        training.extend([line_number])
        training_data['line_'+str(line)+'_'+str(i)] = pd.Series(training)

duration = time.time() - start_time
print('Time taken: ', duration)